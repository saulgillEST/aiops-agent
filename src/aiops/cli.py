import typer
from aiops.agent import plan_task
from aiops.skills import SKILLS
from aiops.tools import resolve_parameters

app = typer.Typer(help="AIOps Agent CLI")

@app.command()
def install(skill_name: str):
    """
    Install a skill by name, asking for missing parameters interactively.
    """
    skill = SKILLS.get(skill_name)
    if not skill:
        typer.echo(f"❌ Skill '{skill_name}' not found")
        return

    typer.echo(f"Running skill: {skill_name}")

    # Resolve parameters interactively
    params = resolve_parameters(skill)

    # Call the skill entrypoint
    next_prompt = skill["entrypoint"](**params)

    # If the skill returned a next task, loop
    while next_prompt:
        typer.echo(f"\nNext task: {next_prompt}")
        if not typer.confirm("Do you want to continue?"):
            break
        params = resolve_parameters(skill)
        next_prompt = skill["entrypoint"](**params)

if __name__ == "__main__":
    app()
