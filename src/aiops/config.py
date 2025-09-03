import os, yaml, pathlib

def read_yaml(path):
    if not path.exists(): return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def get_api_key(cfg):
    v = cfg.get("llm", {}).get("api_key")
    if not v: return None
    if v.startswith("ENV:"):
        return os.environ.get(v.split(":",1)[1])
    return v
