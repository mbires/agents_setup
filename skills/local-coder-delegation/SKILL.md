---
name: local-coder-delegation
version: 3.0.0
description: >-
  Use before coding any sub-task yourself when the local-coder MCP (delegate_code_task) is
  connected: helpers, parsers, validators, DTOs, type fixes, docstrings, small bug fixes or
  unit tests in 1-3 files. What to delegate, how to call, review and retry.
---

# Local Coder Delegation

Tool: Claude `mcp__local-coder__delegate_code_task`; Codex/Gemini `delegate_code_task`. Only `IMPLEMENT` and `TEST` are enabled; others return `TASK_TYPE_DISABLED` (if TRIAGE/REVIEW were enabled, read `reference.md`). Local Coder never touches the real project; you apply approved patches yourself.

## 1. When

Judge each sub-task, not the feature: complex features still contain delegatable leaves. Delegate when: output and its shape are clear; ≤3 writable files, target and context files known; no security/crypto/auth, destructive migration or complex concurrency; a test target exists or can be made (§3).

Candidates: pure helpers, enum/value mappings, DTO conversion, parsers with offline fixtures, formatting, validators, methods behind defined interfaces, type fixes, docstrings, small bug fixes with failing tests, unit tests, boilerplate models.

Never: architecture, auth/credentials, crypto/hashing, migrations with data, concurrency, payments, deployment/CI, MCP security boundaries, spec changes, broad ambiguous debugging.

Must: healthy Local Coder + ≥1 suitable sub-task → ≥1 real call (several in larger phases). Past infra failures are no excuse once healthy. Zero delegations in a phase → report each candidate with its rejection reason.

## 2. Call

Find paths by file list or grep; don't read whole files into your context. `task`: exact names and requirements. `project_root`: absolute. `writable_files`: 1-3 (TEST: test/fixture files only). `context_files`: 0-6. `verbose=true` only for debugging.

```json
{"task": "Add normalize_name(s: str) -> str to src/utils/text.py: strip, collapse whitespace, casefold.",
 "project_root": "D:/proj", "task_type": "IMPLEMENT", "writable_files": ["src/utils/text.py"],
 "verification": {"runner": "pytest", "targets": ["tests/unit/test_text.py"]}}
```

## 3. Verification = runner + test file, never a command

`runner`: `pytest`, `ruff_check`, `ruff_format`, `mypy`, `none`. `targets`: 1-5 relative paths that exist or are in `writable_files`. Never `.`, `python -c`, flags or `::test` node IDs: they fail with `invalid_request` and the patch returns unverified.

Test target, best first: existing test → small test you write (model can't fit it to its own bug) → delegate `TEST` first, review, then `IMPLEMENT` → last resort, new test in `writable_files` (check its assertions).

Examples only in `task` never run: put them plus edge cases (separators, repeated spaces, empty, non-ASCII) in the test. No behavior (types, docstrings): `mypy`/`ruff_check` on changed files. `none` = unverified; check yourself before applying.

## 4. Review

Result: `status` (`success`, `verification_failed`, `rejected`, `no_change`, error + `error_code`), `files_changed`, `patch` (MCP-computed diff), `verification` (runner output with `stdout_tail` on failure, never model-authored), `model_result`, `warnings`.

1. Diff touches only expected files/lines.
2. Check `verification` and `warnings`; in TEST, `TEST_CORRECTLY_EXPOSES_DEFECT` is valid.
3. No unwanted imports, side effects, anti-patterns; a pass doesn't prove design validity.
4. Apply approved patches yourself.

## 5. Retry

- Max 2 attempts per task; retry once with the concrete failure (read `stdout_tail`; an auto-repair may have run). Then implement directly. Never loop.
- `invalid_request` on a target is your error: fix and resend, not an attempt.
- Infra error (LM Studio/MCP down, timeout) is not an attempt: ≤1 passive health check, else skip Local Coder for the phase. No restarts, model reloads or repeated probes.
- Passive = no inference: server connected, tool listed, model availability, or `local-coder-mcp doctor` if it doesn't generate. Never probe with `1+1=` or `hello`.

## 6. Design

Prefer cohesive modules with narrow interfaces so a change needs ~1 writable file, 1-3 context files and one test. Split by responsibility, never just for size; no LOC quotas.
