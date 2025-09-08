import typer
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()  # automatically loads variables into os.environ
# Optional: fallback if key not set
if "OPENAI_API_KEY" not in os.environ:
    print("Warning: OPENAI_API_KEY not found. Some features will not work.")

from .orchestrator import run_session
from .llm.openai_client import OpenAIClient
from .skills_loader import load_skill_context
from .retrieval import fetch_urls_from_text, fetch_text
from .config import load_config
from .state_manager import StateManager

app = typer.Typer(help="AIOps conversational agent")

@app.command("start")
def start(
        reset: bool = typer.Option(
            False,
            "--reset",
            help="Clear conversation history before starting",
        )
):
    cfg = load_config()
    provider = cfg.get("llm", {}).get("provider", "openai")
    model = cfg.get("llm", {}).get("model", "gpt-4o-mini")
    api_env = cfg.get("llm", {}).get("api_key_env", "OPENAI_API_KEY")
    if provider == "openai":
        llm = OpenAIClient(model, api_key_env=api_env)
    else:
        raise typer.Exit("LLM provider not supported in v1")

    skill_ctx = load_skill_context()

    state = StateManager(persistent=cfg.get('session',{}).get('persistent_memory', True),
                         workspace_dir=cfg.get('execution',{}).get('working_dir','./.aiops_workspace'))

    if reset:
        state.clear()
        print("Conversation history cleared.")

    print("🤖 AIOps Agent ready. Type 'exit' or Ctrl-D to quit.")
    try:
        while True:
            p = input("aiops> ").strip()
            if not p:
                continue
            if p.lower() in ("exit","quit"):
                print("Goodbye.")
                break
            urls = fetch_urls_from_text(p)
            docs = []
            for u in urls:
                try:
                    docs.append(fetch_text(u))
                except Exception as e:
                    print(f"Warning: couldn't fetch {u}: {e}")
            run_session(llm, skill_ctx, "\n\n".join(docs), [p], cfg, state)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
if __name__ == '__main__':
    app()