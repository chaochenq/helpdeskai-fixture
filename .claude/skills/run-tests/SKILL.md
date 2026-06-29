---
name: run-tests
description: Install dependencies and run the test suite. Use when asked to run tests, verify a change, or check CI status locally.
allowedTools:
  - bash
  - read
---

# Run tests

Install dependencies and run the unit test suite for HelpDeskAI.

## Steps

1. Install dependencies (first run only): `poetry install`
2. Run the suite: `poetry run pytest tests/ -v`
3. If a test fails, read the failing test and the code under test, summarize the
   root cause, and propose a fix. Do not modify a test to make it pass without
   understanding why it failed.

## Scope

Tests live in `tests/`. They use mocked LLM/AWS calls and do not require network
access or real credentials.
