---
name: security-review
description: Run a security review of the current branch's changes using Trent's AppSec advisor before opening or merging a PR. Use when asked to security-review a diff, check for vulnerabilities, or gate a merge.
allowedTools:
  - bash
  - read
  - mcp__trent__security_advisor
  - mcp__trent__scan_local_diff
---

# Security review

Review the pending changes on the current branch for security issues before they merge.

## Steps

1. Get the diff against the base branch:
   ```bash
   git fetch origin main
   git diff origin/main...HEAD
   ```
2. Pass the diff and a short description of the change to Trent's AppSec advisor
   (the `trent` MCP server) via `mcp__trent__security_advisor`, or run
   `mcp__trent__scan_local_diff` to scan the uncommitted/working changes.
3. Pay special attention to this repo's load-bearing invariants (see `CLAUDE.md`):
   tenant scoping on every data-layer access, parameterized SQL, no PII in logs,
   no committed secrets, least-privilege IAM.
4. Summarize findings by severity. **Block the merge on any High or Critical finding**
   until it is fixed or explicitly risk-accepted by a reviewer.

## Notes

Trent authenticates via OAuth (browser, tokens in the OS keychain) — there is no API
key to configure here. Never paste secrets into the prompt.
