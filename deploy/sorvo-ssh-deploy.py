#!/usr/bin/python3
"""SSH forced command: only deploy a full main-branch commit SHA."""
import os
import re
import subprocess
import sys

command = os.environ.get("SSH_ORIGINAL_COMMAND", "")
match = re.fullmatch(r"deploy ([0-9a-f]{40})", command)
if not match:
    sys.exit("Only 'deploy <40-character commit SHA>' is permitted")
env = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/var/lib/sorvo-deploy",
    "GIT_TERMINAL_PROMPT": "0",
    "LANG": "C.UTF-8",
}
try:
    result = subprocess.run(
        ["/usr/local/lib/sorvo-deploy.py", match.group(1)],
        env=env, timeout=180, check=False,
    )
except subprocess.TimeoutExpired:
    sys.exit("Deployment exceeded 180 seconds; inspect server logs before retrying")
sys.exit(result.returncode)
