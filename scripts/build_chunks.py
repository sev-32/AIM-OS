import json
from datetime import datetime, UTC
from pathlib import Path
from typing import List, Dict

try:
    import tiktoken
except ImportError:
    tiktoken = None

MAX_TOKENS = 900
OVERLAP_LINES = 6
PLAN_PATH = Path('analysis/PLAN.md')
SUMMARY_DIR = Path('analysis/summaries')
DEEP_DIR = SUMMARY_DIR / 'deep'
CHUNK_DIR = Path('analysis/chunks')
REGISTRY_PATH = CHUNK_DIR / 'index.json'
SNAPSHOT_PATH = CHUNK_DIR / 'snapshots.json'
DEPENDENCY_PATH = CHUNK_DIR / 'dependencies.json'
ENCODING_NAME = 'cl100k_base'

TAG_KEYWORDS = {
    'CMC': 'CMC',
    'APOE': 'APOE',
    'VIF': 'VIF',
    'SDF-CVF': 'SDF-CVF',
    'SEG': 'SEG',
    'Idea': 'IDEA',
    'κ': 'KAPPA',
}


def get_token_count(text: str) -> int:
    if not text:
        return 0
    if tiktoken is None:
        return len(text.split())
    enc = tiktoken.get_encoding(ENCODING_NAME)
    return len(enc.encode(text))


def chunk_text(text: str, max_tokens: int, overlap_lines: int) -> List[str]:
    lines = text.splitlines()
    chunks: List[str] = []
    buffer: List[str] = []
    token_total = 0
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        line_tokens = get_token_count(line)
        if buffer and token_total + line_tokens > max_tokens:
            chunks.append('\n'.join(buffer).strip())
            # start new buffer with overlap
            buffer = buffer[-overlap_lines:] if overlap_lines > 0 else []
            token_total = sum(get_token_count(l) for l in buffer)
        buffer.append(line)
        token_total += line_tokens
        idx += 1
    if buffer:
        chunks.append('\n'.join(buffer).strip())
    return [chunk for chunk in chunks if chunk]


def detect_headings(chunk: str) -> List[str]:
    headings = []
    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped.startswith('#'):
            headings.append(stripped)
    return headings


def detect_tags(chunk: str) -> List[str]:
    tags = {tag for keyword, tag in TAG_KEYWORDS.items() if keyword in chunk}
    return sorted(tags)


def ensure_dirs():
    SUMMARY_DIR.mkdir(exist_ok=True)
    DEEP_DIR.mkdir(exist_ok=True)
    CHUNK_DIR.mkdir(exist_ok=True)


def write_summary(path: Path, title: str, body: str):
    path.write_text(f'{title}\n\n{body}\n', encoding='utf-8')


def collect_summary_entries() -> List[Dict]:
    entries = []
    for level, rel_path in [
        ('overview', SUMMARY_DIR / 'overview.md'),
        ('mid', SUMMARY_DIR / 'mid.md'),
    ]:
        if rel_path.exists():
            text = rel_path.read_text(encoding='utf-8')
            entries.append({
                'id': level,
                'path': str(rel_path),
                'tokens_estimated': get_token_count(text),
                'level': level
            })
    if DEEP_DIR.exists():
        for path in sorted(DEEP_DIR.glob('*.md')):
            text = path.read_text(encoding='utf-8')
            entries.append({
                'id': path.stem,
                'path': str(path),
                'tokens_estimated': get_token_count(text),
                'level': 'deep'
            })
    return entries


def load_optional(path: Path) -> Dict[str, Dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            return {}
    return {}


def update_registry(chunks: List[Dict], summaries: List[Dict]):
    registry = {
        'generated_at': datetime.now(UTC).isoformat(),
        'chunks': chunks,
        'summaries': summaries,
    }
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')


def build():
    if not PLAN_PATH.exists():
        raise SystemExit('PLAN.md not found')

    ensure_dirs()

    text = PLAN_PATH.read_text(encoding='utf-8')
    total_tokens = get_token_count(text)

    words = text.split()
    overview_limit = min(total_tokens, MAX_TOKENS)
    mid_limit = min(total_tokens, MAX_TOKENS * 4)
    overview_text = ' '.join(words[:overview_limit])
    mid_text = ' '.join(words[:mid_limit])

    write_summary(SUMMARY_DIR / 'overview.md', '# Overview', overview_text)
    write_summary(SUMMARY_DIR / 'mid.md', '# Mid-Tier Summary', mid_text)

    snapshot_meta = load_optional(SNAPSHOT_PATH)
    dependency_meta = load_optional(DEPENDENCY_PATH)

    raw_chunks = chunk_text(text, MAX_TOKENS, OVERLAP_LINES)
    chunk_entries = []
    for idx, chunk in enumerate(raw_chunks, start=1):
        chunk_id = f'plan_chunk_{idx:02d}'
        chunk_path = CHUNK_DIR / f'{chunk_id}.md'
        chunk_path.write_text(f'# PLAN Chunk {idx}\n\n{chunk}\n', encoding='utf-8')
        entry = {
            'id': chunk_id,
            'path': str(chunk_path),
            'tokens_estimated': get_token_count(chunk),
            'source': 'analysis/PLAN.md',
            'headings': detect_headings(chunk),
            'tags': detect_tags(chunk),
        }
        if chunk_id in snapshot_meta:
            entry['snapshots'] = snapshot_meta[chunk_id]
        if chunk_id in dependency_meta:
            entry['dependencies'] = dependency_meta[chunk_id]
        chunk_entries.append(entry)

    summary_entries = collect_summary_entries()
    update_registry(chunk_entries, summary_entries)


if __name__ == '__main__':
    build()
