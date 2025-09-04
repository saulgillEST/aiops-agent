import subprocess

def run_cmd(cmd: str, live: bool = True) -> int:
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    if live:
        for line in proc.stdout:
            print(line, end="")
    return proc.wait()

def confirm(prompt: str) -> bool:
    resp = input(f"{prompt} [y/N]: ").strip().lower()
    return resp in ("y", "yes")

def resolve_parameters(skill):
    """
    Ask the user for any required parameters that were not provided.
    """
    params = {}
    for name, desc in skill["parameters"].items():
        value = None
        while not value:
            value = input(f"Please provide {name} ({desc}): ").strip()
        params[name] = value
    return params

