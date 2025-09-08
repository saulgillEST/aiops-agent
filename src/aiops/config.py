import toml
from pathlib import Path

DEFAULT_CONFIG = {
    "execution": {
        "run_mode": "ask",        # ask | auto
        "shell": "/bin/bash",
        "working_dir": "./.aiops_workspace",
        "sandbox": None           # "docker" or None
    },
    "llm": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY"
    },
    "session": {
        "persistent_memory": True,
        "max_log_files": 10,
        "max_log_size_mb": 10
    },
    "fetch": {
        "allow_live_web": True
    }
}

def load_config(path: str = "../aiops.toml") -> dict:
    p = Path(path)
    if p.exists():
        try:
            user_cfg = toml.load(p)
            return merge_dicts(DEFAULT_CONFIG, user_cfg)
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def merge_dicts(base, override):
    for k, v in override.items():
        if isinstance(v, dict) and k in base:
            base[k] = merge_dicts(base[k], v)
        else:
            base[k] = v
    return base