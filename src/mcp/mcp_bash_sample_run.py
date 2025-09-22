from rich.console import Console
from rich.syntax import Syntax
import asyncio

console = Console()

def display_bash(script: str):
    syntax = Syntax(script, "bash", line_numbers=True, indent_guides=True)
    console.print(syntax)

async def main():
    # Imagine this script came from your LLM
    generated_script = """#!/usr/bin/env bash
echo "Hello from MCP!"
"""

    console.print("[bold green]Generated script:[/bold green]")
    display_bash(generated_script)

    confirm = input("Run this script via MCP? [y/N] ")
    if confirm.lower().startswith("y"):
        from app import run_script_via_mcp
        result = await run_script_via_mcp(generated_script)
        console.print(f"[bold cyan]Exit Code:[/bold cyan] {result['exit_code']}")
        console.print(f"[bold cyan]STDOUT:[/bold cyan]\n{result['stdout']}")
        console.print(f"[bold cyan]STDERR:[/bold cyan]\n{result['stderr']}")

if __name__ == "__main__":
    asyncio.run(main())
