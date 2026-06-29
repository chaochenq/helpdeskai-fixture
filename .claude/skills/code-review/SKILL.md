---
name: code-review
description: Review the current branch's diff for correctness, readability, and adherence to repo conventions. Use when asked to review code, a PR, or a diff.
allowedTools:
  - bash
  - read
---

# Code review

Review the pending changes on the current branch.

## Steps

1. Get the diff: `git fetch origin main && git diff origin/main...HEAD`
2. Review for: correctness bugs, missing error handling, unclear naming, and any
   deviation from the conventions in `CLAUDE.md` (tenant scoping, parameterized SQL,
   no PII logging, no committed secrets).
3. For anything security-relevant, hand off to the `security-review` skill rather than
   judging it here.
4. Produce a concise review: blocking issues first, then non-blocking suggestions.
   Reference specific `file:line` locations.

## Notes

This skill is read-only — it does not modify code. It proposes changes for a human or a
follow-up edit to apply.
