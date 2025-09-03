import os
import subprocess
from pathlib import Path
import typer
from openai import OpenAI

client = OpenAI()

def run(repo_url: str, ref: str = "main", readme_rel_path: str = "README.md"):
    """
    Clone a repo, read a user-specified README, generate + execute install script,
    report success/failure, and ask for next instructions.
    """
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_dir = Path.cwd() / repo_name

    try:
        # Clone or update
        if not clone_dir.exists():
            typer.echo(f"📥 Cloning {repo_url} into {clone_dir}...")
            subprocess.run(["git", "clone", "--branch", ref, repo_url, str(clone_dir)], check=True)
        else:
            typer.echo(f"🔄 Updating existing repo {repo_name}...")
            subprocess.run(["git", "-C", str(clone_dir), "fetch", "origin", ref], check=True)
            subprocess.run(["git", "-C", str(clone_dir), "checkout", ref], check=True)
            subprocess.run(["git", "-C", str(clone_dir), "pull"], check=True)

        # Read README
        readme_path = clone_dir / readme_rel_path
        if not readme_path.exists():
            typer.echo(f"❌ File not found: {readme_path}")
            return troubleshoot_task(f"Missing file: {readme_path}")

        readme_text = readme_path.read_text()

        # Ask LLM to generate install script
        messages = [
            {"role": "system", "content": "Generate safe, idempotent Bash scripts for Ubuntu."},
            {"role": "user", "content": f"Generate an install script based on this README:\n{readme_text}"}
        ]
        response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        script = response.choices[0].message.content.strip()

        script_path = clone_dir / "install.sh"
        script_path.write_text(script)
        os.chmod(script_path, 0o755)
        typer.echo(f"\nGenerated script saved at {script_path}\n")

        # Ask user to execute
        if typer.confirm("Do you want to execute this script now?"):
            result = subprocess.run(["bash", str(script_path)], capture_output=True, text=True)
            typer.echo(result.stdout)
            typer.echo(result.stderr)
            success = result.returncode == 0
        else:
            success = None
            typer.echo("⚠️ Script not executed.")

        # Handle success/failure
        if success:
            typer.echo("✅ Task completed successfully!")
            next_task = input("What would you like me to do next? (press enter to skip) > ").strip()
            return next_task
        elif success is False:
            return troubleshoot_task(result.stdout + "\n" + result.stderr)
        else:
            # Script not executed
            return input("⚠️ Task not executed. What should I do next? > ").strip()

    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Command failed: {e}")
        return troubleshoot_task(str(e))

# Helper function for troubleshooting
def troubleshoot_task(logs: str):
    """
    Analyze logs and suggest troubleshooting steps using LLM.
    """
    typer.echo("🔍 Task failed or incomplete. Analyzing logs for troubleshooting...")

    messages = [
        {"role": "system", "content": "You are an AI Ops agent that troubleshoots failed commands."},
        {"role": "user", "content": f"Here are the logs from the failed task:\n{logs}\nSuggest actionable steps to fix or retry the task."}
    ]
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    suggestion = response.choices[0].message.content.strip()
    typer.echo(f"\n💡 Suggested troubleshooting steps:\n{suggestion}\n")

    action = input("Do you want to retry, skip, or provide a manual instruction? > ").strip()
    return action

# Metadata for skill discovery
skill = {
    "name": "install_from_repo",
    "description": "Clone a repo, read a user-specified README, generate/run install script, report success/failure, troubleshoot if failed, and ask next steps.",
    "parameters": {
        "repo_url": "GitHub repository URL",
        "ref": "Branch, tag, or commit (default: main)",
        "readme_rel_path": "Relative path to README or install instructions inside the repo"
    },
    "entrypoint": run
}
