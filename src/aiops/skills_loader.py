from pathlib import Path
def load_skill_context(skills_dir: str = None):
    base = Path(__file__).parent
    skills_path = base / 'skills' if skills_dir is None else Path(skills_dir)
    buf = []
    for p in sorted(skills_path.glob('*.md')):
        try:
            buf.append(p.read_text())
        except Exception:
            pass
    return '\n\n'.join(buf)