import os
import subprocess
import typer

skill = {
    "name": "install_from_repo",
    "description": "Clone a repo, parse README, generate/run install script",
    "parameters": {
        "repo_url": "GitHub repository URL",
        "ref": "Branch, tag, or commit (default: main)",
        "readme_rel_path": "Relative path to README"
    },
    "entrypoint": None  # will assign below
}

def run(repo_url: str, ref: str = "main", readme_rel_path: str = "README.md") -> str:
    """
    Clone the repo, read README instructions, run installation script.
    Returns a next_task prompt or empty string if done.
    """
    try:
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if not os.path.exists(repo_name):
            typer.echo(f"📥 Cloning {repo_url} (ref: {ref})...")
            subprocess.run(
                ["git", "clone", "--branch", ref, repo_url],
                check=True
            )
        else:
            typer.echo(f"Repository {repo_name} already exists, skipping clone.")

        readme_path = os.path.join(repo_name, readme_rel_path)
        if not os.path.exists(readme_path):
            typer.echo(f"❌ README not found at {readme_path}")
            return ""

        # For simplicity, we assume the README has instructions in shell commands
        typer.echo(f"📖 Reading instructions from {readme_path}...")
        with open(readme_path) as f:
            lines = f.readlines()

        # Extract shell commands (simple heuristic: lines starting with "$" or no prompt)
        commands = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("$"):
                line = line[1:].strip()
            commands.append(line)

        if not commands:
            typer.echo("❌ No commands found in README")
            return ""

        # Write a temporary install script
        script_path = os.path.join(repo_name, "install.sh")
        with open(script_path, "w") as f:
            f.write("\n".join(commands))

        # Make it executable
        os.chmod(script_path, 0o755)

        # Ask user if they want to execute
        if typer.confirm(f"Do you want to execute the install script {script_path}?"):
            typer.echo("⚡ Running installation script...")
            result = subprocess.run([script_path], check=False)
            if result.returncode == 0:
                typer.echo("✅ Installation completed successfully!")
                # Ask for next task
                next_task = input("What would you like me to do next? (press enter to finish): ")
                return next_task.strip()
            else:
                typer.echo("❌ Installation failed.")
                return ""
        else:
            typer.echo("Installation skipped by user.")
            return ""
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error during execution: {e}")
        return ""
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}")
        return ""

# Assign entrypoint
skill["entrypoint"] = run
