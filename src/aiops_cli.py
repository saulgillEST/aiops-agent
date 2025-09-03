import typer
from aiops.agent import plan_task
from aiops.skills import SKILLS

app = typer.Typer(help="AIOps Agent CLI")

@app.command()
def install(prompt: str):
    """
    Prompt-driven install command. The agent will select and run skills.
    """
    while True:
        plan = plan_task(prompt)
        typer.echo(f"\nPlan summary: {plan['summary']}\n")

        for a in plan.get("actions", []):
            kind, cmd, params = a.get("run"), a.get("cmd"), a.get("params", {})
            if kind == "skill":
                skill = SKILLS.get(cmd)
                if not skill:
                    typer.echo(f"❌ Skill {cmd} not found")
                    continue
                next_input = skill["entrypoint"](**params)
                if next_input:
                    prompt = next_input  # update prompt for next iteration
            else:
                typer.echo(f"Unknown action type: {kind}")
        # Ask if user wants to continue
        if not typer.confirm("Do you want to continue with further instructions?"):
            break

if __name__ == "__main__":
    app()
