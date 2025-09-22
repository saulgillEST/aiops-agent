# mcp_server.py
from fastmcp import FastMCP
import subprocess
import tempfile
import os

mcp = FastMCP()

@mcp.tool()
def run_bash(script: str) -> dict:
    """
    Run a bash script locally and return output.
    Args:
        script (str): The bash script contents.
    Returns:
        dict: { "exit_code": int, "stdout": str, "stderr": str }
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".sh") as f:
        f.write(script)
        f.flush()
        script_path = f.name

    # Make executable
    os.chmod(script_path, 0o755)

    try:
        result = subprocess.run(
            ["bash", script_path],
            capture_output=True,
            text=True,
            timeout=120  # prevent runaway
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    finally:
        os.remove(script_path)

if __name__ == "__main__":
    # Starts the MCP server (listening on stdio or socket depending on runtime)
    mcp.run()
