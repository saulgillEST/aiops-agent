from fastmcp import StdioClient
import asyncio
import subprocess

async def connect_to_mcp():
    # Spawn the server
    server = subprocess.Popen(
        ["python", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    client = StdioClient(stdin=server.stdin, stdout=server.stdout)

    await client.start()
    return client, server

async def run_script_via_mcp(script: str):
    client, server = await connect_to_mcp()
    try:
        result = await client.call_tool("run_bash", {"script": script})
        return result
    finally:
        server.kill()
