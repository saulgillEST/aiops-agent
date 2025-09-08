import json
from pathlib import Path
import time

class StateManager:
    def __init__(self, persistent=True, workspace_dir="./.aiops_workspace"):
        self.persistent = persistent
        self.workspace = Path(workspace_dir)
        self.state_file = self.workspace / "state.json"
        self.state = {"history": [], "variables": {}}
        if self.persistent:
            self.load()

    def add_message(self, role: str, content: str):
        self.state["history"].append({"role": role, "content": content, "ts": time.time()})
        if self.persistent:
            self.save()

    def set_var(self, key: str, value):
        self.state["variables"][key] = value
        if self.persistent:
            self.save()

    def get_var(self, key: str, default=None):
        return self.state["variables"].get(key, default)

    def load(self):
        if self.state_file.exists():
            try:
                self.state = json.loads(self.state_file.read_text())
            except Exception:
                self.state = {"history": [], "variables": {}}

    def save(self):
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def clear(self):
        self.state = {"history": [], "variables": {}}
        if self.persistent:
            self.save()
