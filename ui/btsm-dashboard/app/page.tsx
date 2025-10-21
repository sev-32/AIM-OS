"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  forceCenter,
  forceLink,
  forceManyBody,
  forceSimulation,
  SimulationNodeDatum,
} from "d3-force";
import { Zoom } from "@visx/zoom";
import type { TransformMatrix } from "@visx/zoom/lib/types";

type MpdNode = {
  mpd_id: string;
  type: string;
  purpose: string;
  manager_of: string[];
  depends_on: string[];
  owners: string[];
  policy_pack_ids: string[];
  max_dependency_degree: number;
};

type MpdEdge = {
  source_id: string;
  target_id: string;
  relation: string;
};

type KpiMap = Record<string, string | number>;

type LayoutNodeDatum = SimulationNodeDatum & { id: string };

type BlastEdge = {
  source_id: string;
  target_id: string;
  relation: string;
  policy_pack_ids: string[];
};

type BlastViolation = {
  kind: "node_policy" | "edge_policy" | "missing_node";
  subject_id: string;
  message: string;
  policy_pack_ids: string[];
};

type BlastRadius = {
  root_ids: string[];
  required_policy_pack_ids: string[];
  impacted_nodes: string[];
  traversed_edges: BlastEdge[];
  violations: BlastViolation[];
  compliant: boolean;
};

const GRAPH_WIDTH = 720;
const GRAPH_HEIGHT = 480;

export default function Home() {
  const apiBase = process.env.NEXT_PUBLIC_BTSM_API ?? "http://localhost:8000";
  const [nodes, setNodes] = useState<MpdNode[]>([]);
  const [edges, setEdges] = useState<MpdEdge[]>([]);
  const [kpis, setKpis] = useState<KpiMap>({});
  const [ownerFilter, setOwnerFilter] = useState<string>("all");
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [error, setError] = useState<string | null>(null);
  const [lifecycleFilter, setLifecycleFilter] = useState<string>("all");
  const [policyFilter, setPolicyFilter] = useState<string>("");
  const [policyMatchMode, setPolicyMatchMode] = useState<"all" | "any">("all");
  const [blastRoot, setBlastRoot] = useState<string | null>(null);
  const [blastRadius, setBlastRadius] = useState<BlastRadius | null>(null);
  const [blastLoading, setBlastLoading] = useState<boolean>(false);
  const [blastError, setBlastError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const lifecycleParam =
          lifecycleFilter !== "all" && lifecycleFilter.trim().length ? lifecycleFilter.trim() : null;
        const policyValues = policyFilter
          .split(/[,\s]+/)
          .map((value) => value.trim())
          .filter((value) => value.length > 0);
        const nodeParams = new URLSearchParams();
        if (lifecycleParam) {
          nodeParams.append("lifecycle", lifecycleParam);
        }
        if (policyValues.length) {
          policyValues.forEach((value) => nodeParams.append("policy_pack_ids", value));
          nodeParams.append("policy_match", policyMatchMode);
        }
        const nodesUrl = nodeParams.toString()
          ? `${apiBase}/mpd/nodes?${nodeParams.toString()}`
          : `${apiBase}/mpd/nodes`;

        const edgeParams = new URLSearchParams();
        if (policyValues.length) {
          policyValues.forEach((value) => edgeParams.append("policy_pack_ids", value));
          edgeParams.append("policy_match", policyMatchMode);
        }
        const edgesUrl = edgeParams.toString()
          ? `${apiBase}/mpd/edges?${edgeParams.toString()}`
          : `${apiBase}/mpd/edges`;

        const [nodesRes, edgesRes, kpiRes] = await Promise.all([
          fetch(nodesUrl),
          fetch(edgesUrl),
          fetch(`${apiBase}/kpis`),
        ]);
        if (!nodesRes.ok || !edgesRes.ok || !kpiRes.ok) {
          throw new Error("Failed to fetch BTSM data");
        }
        const [nodesJson, edgesJson, kpisJson] = await Promise.all([
          nodesRes.json(),
          edgesRes.json(),
          kpiRes.json(),
        ]);
        setNodes(nodesJson);
        setEdges(edgesJson);
        setKpis(kpisJson);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }
    loadData();
  }, [apiBase, lifecycleFilter, policyFilter, policyMatchMode]);

  const preferredRootId = useMemo(() => {
    if (!nodes.length) {
      return null;
    }
    const trunk = nodes.find((node) => node.mpd_id === "aimos.mige.trunk");
    if (trunk) {
      return trunk.mpd_id;
    }
    return nodes[0]?.mpd_id ?? null;
  }, [nodes]);

  useEffect(() => {
    if (!nodes.length) {
      setBlastRoot(null);
      setBlastRadius(null);
      return;
    }
    setBlastRoot((current) => {
      if (current && nodes.some((node) => node.mpd_id === current)) {
        return current;
      }
      return preferredRootId;
    });
  }, [nodes, preferredRootId]);

  useEffect(() => {
    if (!blastRoot) {
      setBlastRadius(null);
      return;
    }
    const controller = new AbortController();
    let cancelled = false;
    async function loadBlast() {
      setBlastLoading(true);
      setBlastError(null);
      try {
        const response = await fetch(`${apiBase}/mpd/blast-radius`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ root_ids: [blastRoot] }),
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Blast radius request failed (${response.status})`);
        }
        const payload = (await response.json()) as BlastRadius;
        if (!cancelled) {
          setBlastRadius(payload);
        }
      } catch (err) {
        if (cancelled || (err instanceof DOMException && err.name === "AbortError")) {
          return;
        }
        setBlastRadius(null);
        setBlastError(err instanceof Error ? err.message : "Unknown blast-radius error");
      } finally {
        if (!cancelled) {
          setBlastLoading(false);
        }
      }
    }
    loadBlast();
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [apiBase, blastRoot]);

  const ownerOptions = useMemo(() => {
    const owners = new Set<string>();
    nodes.forEach((node) => node.owners.forEach((owner) => owners.add(owner)));
    return ["all", ...Array.from(owners).sort()];
  }, [nodes]);

  const filteredNodes = useMemo(() => {
    if (ownerFilter === "all") {
      return nodes;
    }
    return nodes.filter((node) => node.owners.includes(ownerFilter));
  }, [nodes, ownerFilter]);

  const filteredEdges = useMemo(() => {
    const allowed = new Set(filteredNodes.map((node) => node.mpd_id));
    return edges.filter(
      (edge) => allowed.has(edge.source_id) && allowed.has(edge.target_id)
    );
  }, [edges, filteredNodes]);

  const impactedNodes = useMemo(() => {
    if (!blastRadius) {
      return new Set<string>();
    }
    return new Set(blastRadius.impacted_nodes);
  }, [blastRadius]);

  const traversedEdgeIds = useMemo(() => {
    if (!blastRadius) {
      return new Set<string>();
    }
    return new Set(blastRadius.traversed_edges.map((edge) => `${edge.source_id}->${edge.target_id}`));
  }, [blastRadius]);

  const nodeViolationIds = useMemo(() => {
    if (!blastRadius) {
      return new Set<string>();
    }
    return new Set(
      blastRadius.violations.filter((violation) => violation.kind === "node_policy").map((violation) => violation.subject_id)
    );
  }, [blastRadius]);

  const edgeViolationIds = useMemo(() => {
    if (!blastRadius) {
      return new Set<string>();
    }
    return new Set(
      blastRadius.violations.filter((violation) => violation.kind === "edge_policy").map((violation) => violation.subject_id)
    );
  }, [blastRadius]);

  const missingNodeViolations = useMemo(() => {
    if (!blastRadius) {
      return [];
    }
    return blastRadius.violations.filter((violation) => violation.kind === "missing_node");
  }, [blastRadius]);

  useEffect(() => {
    if (!filteredNodes.length) {
      setPositions({});
      return;
    }

    const nodeData: LayoutNodeDatum[] = filteredNodes.map((node) => ({ id: node.mpd_id }));
    const linkData = filteredEdges.map((edge) => ({
      source: edge.source_id,
      target: edge.target_id,
    }));

    const simulation = forceSimulation(nodeData)
      .force("charge", forceManyBody().strength(-220))
      .force("center", forceCenter(GRAPH_WIDTH / 2, GRAPH_HEIGHT / 2))
      .force(
        "link",
        forceLink(linkData)
          .id((datum: { id: string }) => datum.id)
          .distance(180)
          .strength(0.15)
      );

    for (let i = 0; i < 200; i += 1) {
      simulation.tick();
    }

    const nextPositions: Record<string, { x: number; y: number }> = {};
    simulation.nodes().forEach((node) => {
      const datum = node as LayoutNodeDatum;
      nextPositions[datum.id] = {
        x: datum.x ?? GRAPH_WIDTH / 2,
        y: datum.y ?? GRAPH_HEIGHT / 2,
      };
    });
    setPositions(nextPositions);
    simulation.stop();
  }, [filteredNodes, filteredEdges]);

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <header style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <h1 style={{ margin: 0 }}>BTSM Dashboard (Alpha)</h1>
        <label>
          Owner filter:&nbsp;
          <select value={ownerFilter} onChange={(event) => setOwnerFilter(event.target.value)}>
            {ownerOptions.map((owner) => (
              <option key={owner} value={owner}>
                {owner}
              </option>
            ))}
          </select>
        </label>
        <label>
          Lifecycle:&nbsp;
          <select value={lifecycleFilter} onChange={(event) => setLifecycleFilter(event.target.value)}>
            <option value="all">All</option>
            <option value="draft">draft</option>
            <option value="active">active</option>
            <option value="sunset">sunset</option>
          </select>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          Policy filter:&nbsp;
          <input
            type="text"
            value={policyFilter}
            placeholder="policy.foo, policy.bar"
            onChange={(event) => setPolicyFilter(event.target.value)}
            style={{ width: "16rem" }}
          />
        </label>
        <label>
          Match:&nbsp;
          <select
            value={policyMatchMode}
            onChange={(event) => setPolicyMatchMode(event.target.value as "all" | "any")}
            disabled={!policyFilter.trim().length}
          >
            <option value="all">all</option>
            <option value="any">any</option>
          </select>
        </label>
        <label>
          Blast root:&nbsp;
          <select
            value={blastRoot ?? ""}
            onChange={(event) => setBlastRoot(event.target.value || null)}
            disabled={!nodes.length}
          >
            <option value="" disabled>
              Select root
            </option>
            {nodes.map((node) => (
              <option key={node.mpd_id} value={node.mpd_id}>
                {node.mpd_id}
              </option>
            ))}
          </select>
        </label>
        <span style={{ fontSize: "0.85rem", color: blastRadius?.compliant ? "#2b8a3e" : "#c92a2a" }}>
          {blastLoading && "Evaluating policies..."}
          {!blastLoading && blastRadius && (blastRadius.compliant ? "Policy guardrail: PASS" : "Policy guardrail: BLOCK")}
        </span>
      </header>

      {error && (
        <p style={{ color: "crimson" }}>
          Failed to load BTSM data. Ensure the FastAPI service is running on <code>http://localhost:8000</code>.
          <br />({error})
        </p>
      )}

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Topology</h2>
        <Zoom<SVGSVGElement>
          width={GRAPH_WIDTH}
          height={GRAPH_HEIGHT}
          scaleXMin={0.5}
          scaleXMax={4}
          scaleYMin={0.5}
          scaleYMax={4}
          wheelDelta={(event) => -event.deltaY / 500}
        >
          {(zoom) => (
            <>
              <svg
                width={GRAPH_WIDTH}
                height={GRAPH_HEIGHT}
                style={{ border: "1px solid #ddd", background: "#f8f9fa" }}
                ref={zoom.containerRef}
              >
                <rect width={GRAPH_WIDTH} height={GRAPH_HEIGHT} fill="transparent" />
                <g transform={zoom.toString()}>
                  {filteredEdges.map((edge, idx) => {
                    const source = positions[edge.source_id];
                    const target = positions[edge.target_id];
                    if (!source || !target) return null;
                    const edgeId = `${edge.source_id}->${edge.target_id}`;
                    const traversed = blastRadius ? traversedEdgeIds.has(edgeId) : false;
                    const edgeViolation = blastRadius ? edgeViolationIds.has(edgeId) : false;
                    const stroke = edgeViolation ? "#fa5252" : traversed ? "#4c6ef5" : "#adb5bd";
                    const strokeWidth = edgeViolation ? 3 : traversed ? 2.2 : 1.2;
                    const opacity = edgeViolation || traversed ? 0.95 : 0.45;
                    return (
                      <g key={`${edge.source_id}-${edge.target_id}-${edge.relation}-${idx}`}>
                        <line
                          x1={source.x}
                          y1={source.y}
                          x2={target.x}
                          y2={target.y}
                          stroke={stroke}
                          strokeWidth={strokeWidth}
                          opacity={opacity}
                        />
                        <text
                          x={(source.x + target.x) / 2}
                          y={(source.y + target.y) / 2}
                          fill={edgeViolation ? "#c92a2a" : "#495057"}
                          fontSize="10"
                          textAnchor="middle"
                        >
                          {edge.relation}
                        </text>
                      </g>
                    );
                  })}
                  {filteredNodes.map((node) => {
                    const position = positions[node.mpd_id] ?? {
                      x: GRAPH_WIDTH / 2,
                      y: GRAPH_HEIGHT / 2,
                    };
                    const impacted = blastRadius ? impactedNodes.has(node.mpd_id) : true;
                    const violation = blastRadius ? nodeViolationIds.has(node.mpd_id) : false;
                    const isRoot = blastRoot === node.mpd_id;
                    const isActive = activeNode === node.mpd_id;
                    let fill = "#1c7ed6";
                    if (!impacted && blastRadius) {
                      fill = "#ced4da";
                    }
                    if (violation) {
                      fill = "#fa5252";
                    }
                    if (isRoot) {
                      fill = violation ? "#ff6b6b" : "#fd7e14";
                    }
                    if (isActive) {
                      fill = violation ? "#ff8787" : "#fab005";
                    }
                    const stroke = violation ? "#c92a2a" : "#ffffff";
                    return (
                      <g
                        key={node.mpd_id}
                        onMouseEnter={() => setActiveNode(node.mpd_id)}
                        onMouseLeave={() => setActiveNode(null)}
                      >
                        <circle
                          cx={position.x}
                          cy={position.y}
                          r={isActive ? 18 : 14}
                          fill={fill}
                          stroke={stroke}
                          strokeWidth={2.2}
                          style={{ transition: "all 0.15s ease" }}
                        />
                        <text x={position.x} y={position.y - 22} fill="#212529" fontSize="11" textAnchor="middle">
                          {node.mpd_id}
                        </text>
                      </g>
                    );
                  })}
                </g>
              </svg>
              <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem" }}>
                <button type="button" onClick={zoom.reset}>
                  Reset
                </button>
                <button type="button" onClick={zoom.center}>
                  Center
                </button>
              </div>
            </>
          )}
        </Zoom>
        <article style={{ marginTop: "1rem", background: "#f1f3f5", padding: "1rem", borderRadius: "6px" }}>
          <h3 style={{ marginTop: 0 }}>Blast Radius Summary</h3>
          {blastLoading && <p>Evaluating policy guardrail…</p>}
          {!blastLoading && !blastRadius && !blastError && <p>Select a root node to evaluate the blast radius.</p>}
          {blastError && (
            <p style={{ color: "#c92a2a" }}>
              Failed to evaluate blast radius.&nbsp;
              <span style={{ fontSize: "0.85rem" }}>{blastError}</span>
            </p>
          )}
          {!blastLoading && blastRadius && !blastError && (
            <>
              <p style={{ marginBottom: "0.75rem" }}>
                <strong>Root:</strong> {blastRadius.root_ids.join(", ") || "n/a"} &nbsp;•&nbsp;
                <strong>Impacted nodes:</strong> {blastRadius.impacted_nodes.length} &nbsp;•&nbsp;
                <strong>Status:</strong>{" "}
                <span style={{ color: blastRadius.compliant ? "#2b8a3e" : "#c92a2a" }}>
                  {blastRadius.compliant ? "PASS" : "BLOCK"}
                </span>
              </p>
              <p style={{ marginBottom: "0.75rem" }}>
                <strong>Required policy packs:</strong>{" "}
                {blastRadius.required_policy_pack_ids.length
                  ? blastRadius.required_policy_pack_ids.join(", ")
                  : "none"}
              </p>
              {blastRadius.violations.length === 0 ? (
                <p style={{ color: "#2b8a3e", marginBottom: 0 }}>No policy violations detected.</p>
              ) : (
                <div>
                  <strong>Violations ({blastRadius.violations.length}):</strong>
                  <ul style={{ marginTop: "0.5rem", marginBottom: 0 }}>
                    {blastRadius.violations.map((violation) => (
                      <li key={`${violation.kind}-${violation.subject_id}`} style={{ marginBottom: "0.35rem" }}>
                        <strong>{violation.subject_id}</strong>: {violation.message}
                        {violation.policy_pack_ids.length > 0 && (
                          <span style={{ color: "#495057" }}>
                            &nbsp;[{violation.policy_pack_ids.join(", ")}]
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {missingNodeViolations.length > 0 && (
                <p style={{ marginTop: "0.5rem", color: "#c92a2a" }}>
                  {missingNodeViolations.length} downstream node(s) referenced in the graph are missing from the
                  repository.
                </p>
              )}
            </>
          )}
        </article>
        {activeNode && (
          <aside style={{ marginTop: "1rem", background: "#f1f3f5", padding: "1rem", borderRadius: "6px" }}>
            <h3 style={{ marginTop: 0 }}>{activeNode}</h3>
            {filteredNodes
              .filter((node) => node.mpd_id === activeNode)
              .map((node) => (
                <div key={node.mpd_id}>
                  <p>
                    <strong>Type:</strong> {node.type}
                  </p>
                  <p>
                    <strong>Purpose:</strong> {node.purpose}
                  </p>
                  <p>
                    <strong>Owners:</strong> {node.owners.join(", ") || "n/a"}
                  </p>
                  <p>
                    <strong>Policy packs:</strong> {node.policy_pack_ids?.join(", ") || "none"}
                  </p>
                  <p>
                    <strong>Depends on:</strong> {node.depends_on.join(", ") || "none"}
                  </p>
                </div>
              ))}
          </aside>
        )}
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>KPI Metrics</h2>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          {Object.entries(kpis).map(([name, value]) => (
            <div key={name} style={{ background: "#f8f9fa", padding: "0.75rem 1rem", borderRadius: "8px" }}>
              <div style={{ fontSize: "0.75rem", color: "#495057" }}>{name}</div>
              <div style={{ fontWeight: "bold", fontSize: "1.1rem" }}>{String(value)}</div>
              {typeof value === "number" && <Sparkline value={value} />}
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>Next Steps</h2>
        <ul>
          <li>Switch to live visx/Next graph components with hover tooltips and zoom.</li>
          <li>Introduce additional filters (policy packs, lifecycle stage) and highlight blast radius.</li>
          <li>Persist KPI history in the API and chart trends over time.</li>
        </ul>
      </section>
    </main>
  );
}

function Sparkline({ value }: { value: number }) {
  const history = useMemo(() => {
    const base = Math.max(value, 1);
    return [base * 0.75, base * 0.9, base, base * 1.02, base * 0.95, base * 1.08];
  }, [value]);
  const width = 80;
  const height = 28;
  const max = Math.max(...history);
  const min = Math.min(...history);
  const points = history
    .map((point, index) => {
      const x = (index / (history.length - 1 || 1)) * width;
      const y = height - ((point - min) / (max - min || 1)) * height;
      return `${x},${y}`;
    })
    .join(" ");
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polyline
        points={points}
        fill="none"
        stroke="#4c6ef5"
        strokeWidth={2}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}
