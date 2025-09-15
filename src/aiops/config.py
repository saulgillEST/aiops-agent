# src/aiops/config.py

import tomli
from pathlib import Path
from dotenv import load_dotenv
import os
from rich.console import Console

ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Make sure API key is in environment
if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

DEFAULT_CONFIG = {
    "llm": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY"
    },
    "session": {
        "persistent_memory": True
    },
    "execution": {
        "working_dir": "./.aiops_workspace",
        "auto_run_if_confident": False
    }
}


def load_config(config_path: str = "aiops_config.toml"):
    """
    Load configuration from TOML file. If file doesn't exist, use defaults.
    """
    cfg_file = Path(config_path)
    console = Console()
    if cfg_file.exists():
        with open(cfg_file, "rb") as f:
            try:
                cfg = tomli.load(f)
                merged = DEFAULT_CONFIG.copy()
                # Deep merge of nested dicts
                for k, v in cfg.items():
                    if isinstance(v, dict):
                        merged[k].update(v)
                    else:
                        merged[k] = v
                return merged
            except Exception as e:
                console.print(f"⚠️  Failed to parse {config_path}: {e}", style="red")
                return DEFAULT_CONFIG
    else:
        return DEFAULT_CONFIG
