# src/aiops/cli.py

import os
from .llm.openai_client import OpenAIClient
from .state_manager import StateManager
from .orchestrator import Orchestrator
from .config import Config

def main():
    cfg = Config().load_config()
    # Load config (minimal example)
    api_key = os.environ.get(cfg.get("llm", {}).get("api_key_env")) or os.environ.get(
        "OPENAI_API_KEY"
    )
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    model = cfg.get("llm", {}).get("model", "gpt-4o-mini")
    work_dir = cfg.get("execution", {}).get("working_dir", "./.aiops_workspace/")
    state_file = cfg.get("execution", {}).get("state_file", ".aiops_state.json")

    # Init components
    client = OpenAIClient(api_key=api_key, model=model)
    state = StateManager(work_dir + state_file)
    orchestrator = Orchestrator(client, state)

    # Start main loop
    orchestrator.start()


if __name__ == "__main__":
    main()
