from pathlib import Path
import subprocess, tempfile, os

class ScriptWorkspace:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "script.sh"

    def write_new(self, script: str):
        self.path.write_text(script)

    def apply_unified_diff(self, patch: str):
        # attempt to apply patch; fallback to replace file with last 'new' content
        try:
            p = tempfile.NamedTemporaryFile(delete=False, mode='w')
            p.write(patch)
            p.flush()
            p.close()
            res = subprocess.run(['patch','-u', str(self.path), p.name], capture_output=True, text=True)
            if res.returncode != 0:
                parts = patch.split('+++')
                if len(parts) >= 2:
                    new = parts[-1].splitlines()[1:]
                    self.path.write_text('\n'.join(new))
        except Exception:
            self.path.write_text(patch)