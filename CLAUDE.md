# CLAUDE.md — HelpDeskAI

Guidance for Claude Code (and other coding agents) working in this repository.

## Product

HelpDeskAI is a multi-tenant SaaS. Each tenant (a customer company) gets an AI
support agent that answers their end-customers and acts on their behalf (search the
tenant knowledge base, look up orders, issue refunds, create tickets).

## Architecture

- `src/api/` — FastAPI service (`chat`, `kb`, `admin` routers). Entry point: `src.api.app:app`.
- `src/auth/` — JWT validation and tenant-context extraction.
- `src/agent/` — the support agent: a LangGraph orchestrator that delegates to a
  ReAct sub-agent and binds the domain tools in `tools.py`.
- `src/mcp_server/` — a FastMCP server exposing internal tools to the agent.
- `src/data/` — AWS data clients (DynamoDB, RDS/Postgres, S3, Bedrock).
- `infra/` — Terraform for the AWS resources.

## Conventions

- Python 3.11, FastAPI, Pydantic v2. Use `poetry` for deps.
- **Multi-tenancy is the most important invariant.** Every data-layer read and write
  MUST be scoped by the `tenant_id` taken from the *verified JWT claim* (never from a
  request header). Order/customer queries must include a `tenant_id` predicate;
  DynamoDB access must use the `tenant_id` partition key (Query, never Scan-and-filter).
- Never log PII (email, address, card data). Never interpolate untrusted input into SQL —
  use parameterized queries.
- Secrets come from the environment / AWS Secrets Manager, never hardcoded or committed.

## Working with agents in this repo

- **MCP servers** (see `.mcp.json`): `fixture-mcp` (internal tools), `trent` (Trent
  security advisor), `github` (GitHub operations).
- **Skills** (see `.claude/skills/`): `code-review`, `run-tests`, `security-review`,
  `deploy_to_prod`.
- **Before opening or merging a PR, run the `security-review` skill** (it calls Trent's
  `trent-appsec` advisor via the `trent` MCP server) and address any High/Critical
  findings.

## Testing

```bash
poetry install
poetry run pytest tests/ -v
```
