from pathlib import Path
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent

def test_parallel_groups_have_members() -> None:
    flows_dir = BASE_DIR / 'flows'
    parallel = yaml.safe_load((flows_dir / 'parallel_execution.yaml').read_text(encoding='utf-8'))
    for group in parallel['groups']:
        assert len(group['members']) >= 3
