from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional

from packages.seg.witness import write_witness

logger = logging.getLogger("apoe.runner")


class PlanExecutionError(RuntimeError):
    """Raised when plan execution fails."""


def _ensure_workspace(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _split_assignment(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise ValueError(f"Parameter must be key=value, got '{value}'")
    key, raw = value.split("=", 1)
    return key.strip(), raw.strip()


def _coerce_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def parse_params(items: Iterable[str]) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    for item in items:
        key, raw = _split_assignment(item)
        params[key] = _coerce_value(raw)
    return params


def _resolve_path(expr: str, context: Mapping[str, Any]) -> Any:
    parts = expr.split(".")
    current: Any = context
    for part in parts:
        if isinstance(current, Mapping):
            current = current.get(part)
        elif isinstance(current, (list, tuple)):
            try:
                index = int(part)
            except ValueError as exc:
                raise KeyError(f"Cannot index list with '{part}' in path '{expr}'") from exc
            current = current[index]
        else:
            current = getattr(current, part)
    return current


def _replace_tokens(value: str, context: Mapping[str, Any]) -> str:
    result = value
    for token in set(part for part in value.split() if part.startswith("@")):
        path = token[1:]
        try:
            resolved = _resolve_path(path, context)
        except Exception:
            continue
        result = result.replace(token, str(resolved))
    return result


def resolve(value: Any, context: Mapping[str, Any]) -> Any:
    if isinstance(value, str):
        if value.startswith("@"):
            return _resolve_path(value[1:], context)
        if "@" in value:
            return _replace_tokens(value, context)
        return value
    if isinstance(value, Mapping):
        return {k: resolve(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(item, context) for item in value]
    if isinstance(value, tuple):
        return tuple(resolve(item, context) for item in value)
    return value


def _call_module(module_name: str, attr: str, kwargs: Mapping[str, Any]) -> Any:
    module = import_module(module_name)
    func = getattr(module, attr)
    return func(**kwargs)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


class PlanExecutor:
    """Execute an APOE ACL plan."""

    def __init__(
        self,
        plan: Mapping[str, Any],
        *,
        workspace: Path,
        params: Optional[Mapping[str, Any]] = None,
    ):
        self.plan = plan
        self.workspace = _ensure_workspace(workspace)
        self.params = dict(params or {})
        self.context: Dict[str, Any] = {
            "workspace": str(self.workspace),
            "plan": plan,
            "input": {},
            "output": {},
            "result": {},
            "gates": {},
        }

    def _prepare_inputs(self) -> None:
        spec = self.plan.get("inputs", {})
        for key, cfg in spec.items():
            cfg = cfg or {}
            if key in self.params:
                value = self.params[key]
            elif "default" in cfg:
                value = resolve(cfg["default"], self.context)
            elif cfg.get("required", False):
                raise PlanExecutionError(f"Missing required input '{key}'")
            else:
                value = None
            self.context["input"][key] = value
        # carry through params not declared explicitly
        for key, value in self.params.items():
            self.context["input"].setdefault(key, value)

    def _prepare_outputs(self) -> None:
        spec = self.plan.get("outputs", {})
        for key, cfg in spec.items():
            cfg = cfg or {}
            default = cfg.get("default")
            value = resolve(default, self.context) if default is not None else None
            self.context["output"][key] = value

    def _execute_participants(self) -> None:
        for participant in self.plan.get("participants", []) or []:
            module = participant["module"]
            call = participant["call"]
            args = resolve(participant.get("args", {}), self.context)
            logger.debug("Participant %s calling %s.%s", participant.get("name"), module, call)
            result = _call_module(module, call, args)
            result_name = participant.get("result")
            if result_name:
                self.context["result"][result_name] = result
                self.context[result_name] = result

    def _execute_gates(self) -> None:
        for gate in self.plan.get("gates", []) or []:
            module = gate["module"]
            call = gate["call"]
            args = resolve(gate.get("args", {}), self.context)
            gate_id = gate.get("id", call)
            logger.debug("Evaluating gate %s via %s.%s", gate_id, module, call)
            result = _call_module(module, call, args)
            self.context["gates"][gate_id] = result
            self.context["gate"] = result
            passed = getattr(result, "passed", True)
            if not passed:
                for action in gate.get("on_fail", []):
                    self._execute_gate_action(action, gate_id, result)
                raise PlanExecutionError(f"Gate '{gate_id}' failed")

    def _execute_gate_action(self, action: Mapping[str, Any], gate_id: str, result: Any) -> None:
        act = action.get("action")
        params = resolve(action.get("params", {}), {**self.context, "gate": result})
        if act == "abort":
            logger.error("Gate %s requested abort", gate_id)
        elif act == "log":
            level = getattr(logging, str(params.get("level", "info")).upper(), logging.INFO)
            logger.log(level, params.get("message", f"Gate {gate_id} failed"))
        else:
            logger.warning("Unknown gate action '%s' for gate %s", act, gate_id)

    def _execute_step(self, step: Mapping[str, Any]) -> None:
        action = step.get("action")
        params = resolve(step.get("params", {}), self.context)
        if action == "write_json":
            path = Path(params["path"])
            if not path.is_absolute():
                path = self.workspace / path
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = params.get("payload")
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default),
                encoding="utf-8",
            )
            logger.info("Wrote JSON to %s", path)
        elif action == "read_json":
            path = Path(params["path"])
            if not path.is_absolute():
                path = self.workspace / path
            data = json.loads(path.read_text(encoding="utf-8"))
            target = step.get("result")
            if target:
                self.context["result"][target] = data
                self.context[target] = data
        elif action == "write_witness":
            payload = params.get("payload", {})
            filename = params.get("filename", "apoe_plan_witness.jsonl")
            seg_dir = params.get("seg_dir")
            if seg_dir:
                write_witness(payload, seg_dir=Path(seg_dir), filename=filename)
            else:
                write_witness(payload, filename=filename)
        elif action == "log":
            level = getattr(logging, str(params.get("level", "info")).upper(), logging.INFO)
            logger.log(level, params.get("message", ""))
        elif action == "todo":
            logger.warning("TODO: %s", params.get("message", ""))
        elif action == "python":
            code = params.get("code", "")
            exec_env: Dict[str, Any] = {"context": self.context}
            exec(code, exec_env, exec_env)
            result_name = step.get("result")
            if result_name and result_name in exec_env:
                self.context["result"][result_name] = exec_env[result_name]
                self.context[result_name] = exec_env[result_name]
        else:
            logger.warning("Unknown action '%s'", action)

    def _execute_steps(self) -> None:
        for step in self.plan.get("steps", []) or []:
            self._execute_step(step)

    def execute(self) -> Dict[str, Any]:
        self._prepare_inputs()
        self._prepare_outputs()
        self._execute_participants()
        self._execute_gates()
        self._execute_steps()
        return self.context


def execute_plan(
    plan: Mapping[str, Any],
    *,
    workspace: Path,
    params: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    executor = PlanExecutor(plan, workspace=workspace, params=params)
    return executor.execute()


__all__ = ["PlanExecutor", "PlanExecutionError", "execute_plan", "parse_params"]
