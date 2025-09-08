import subprocess
from pathlib import Path

def show_script(path: Path):
    print('\n' + '='*10 + ' Proposed Script ' + '='*10)
    print(path.read_text())
    print('='*34 + '\n')

def run_script(path: Path, shell: str = '/bin/bash', sandbox: str = None):
    content = path.read_text()
    if not content.startswith('#!'):
        content = '#!/usr/bin/env bash\nset -euo pipefail\n\n' + content
        path.write_text(content)
    path.chmod(0o755)
    if sandbox == 'docker':
        cmd = ['docker','run','--rm','-v', f"{str(path.parent)}:/workspace", '-w','/workspace','bash','/bin/bash','/workspace/'+path.name]
        proc = subprocess.run(cmd, capture_output=True, text=True)
    else:
        proc = subprocess.run([shell, str(path)], capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr