from pathlib import Path
import json
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent

def test_pipeline_summary_counts() -> None:
    summary_path = BASE_DIR / 'orchestration_summary.json'
    data = json.loads(summary_path.read_text(encoding='utf-8'))
    assert data['metadata']['agent_count'] >= 20
    assert len(data['edges']) >= 80
    assert sorted(data['policy_summary'])

def test_pipeline_flow_files() -> None:
    flows_dir = BASE_DIR / 'flows'
    main_pipeline = yaml.safe_load((flows_dir / 'main_pipeline.yaml').read_text(encoding='utf-8'))
    assert main_pipeline['stages']
    parallel = yaml.safe_load((flows_dir / 'parallel_execution.yaml').read_text(encoding='utf-8'))
    assert parallel['groups']
