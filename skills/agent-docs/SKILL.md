---
name: agent-docs
version: 1.2.0
description: Rules for creating, structuring, shortening, and updating project/code documentation that is read mainly by AI agents (md files in docs/). Use whenever you write, edit, split, review, translate, condense, or migrate documentation, README/spec/design notes, API or module docs, or when you hand a programming task to another agent and need to reference docs. Also use when docs lack IDs, are too long or wordy, duplicated, stale, or not in English. Trigger even if the user only says "document this", "update the docs", or "add this to the docs".
---

# Agent Docs

Docs are a shared, token-priced resource. Agents read them far more often than they write them. Goal: the smallest doc that lets another agent act correctly, addressable by stable ID so it loads only what it needs.

## Layout

```
docs/
  INDEX.md        # generated. One row per doc: id | path | summary | code paths. Read first.
  GLOSSARY.md     # project terms and abbreviations, max ~50 entries
  <area>/<name>.md
  <area>/INDEX.md # generated only when the project has more than 40 docs
```

Agents never read all docs. Flow: `find <words>` or INDEX.md -> pick IDs -> load only those files or sections (`show ID#sN`).

The index has two levels by itself once there are more than 40 docs (`INDEX_SPLIT` in the script): `INDEX.md` then lists areas (first folder under `docs/`), and each area gets its own `<area>/INDEX.md`. Small projects keep one index. Never write or edit an INDEX.md by hand.

## Doc file format

```markdown
---
id: AUTH-01
title: Login and token refresh
summary: How login, JWT issue and refresh work; read before touching auth/.
code: [src/auth/login.py, src/auth/tokens.py]
status: stable
updated: 2026-11-03
---

## Purpose {#s1}
One or two lines.

## Contract {#s2}
- `verify(user, pw) -> Token | None`; raises `RateLimited` after 5 fails/min.

## Invariants {#s3}
- Tokens expire after 15 min; refresh needs a valid refresh token.

## Gotchas {#s4}
- `tokens.py` caches the signing key at import; restart after rotation.
```

`status` is one of: `draft`, `stable`, `deprecated`. The `summary` is one line that tells an agent when to read the doc.

## IDs (the script makes them, you do not)

- Never invent or edit IDs by hand. New doc: `python scripts/docs_tool.py new <relpath> "<title>"`. Existing md files without IDs: `python scripts/docs_tool.py init`. The script picks the prefix from the folder name and the next free number.
- Doc ID looks like `AUTH-01`. Section ID `{#sN}` sits on each `##` heading. `###` headings need no ID.
- IDs are never reused, renamed, or renumbered. New section gets the next free number. Deleted section: its number is retired.
- When you add a `##` section by hand, give it the next free `{#sN}`; `lint` catches mistakes.
- Reference format everywhere (docs, tasks, code comments, commits): `AUTH-01` or `AUTH-01#s3`.
- Moving or renaming a file keeps its ID. Only the path in INDEX.md changes (`index` does that).

## Language and words

- Write all docs in English, even if the user or the old docs use another language. Keep identifiers, file names, commands, and error messages exactly as in the code.
- Use plain, everyday words. Prefer the short common word: "use" not "utilize", "start" not "initiate", "so" not "consequently", "check" not "verify" (unless `verify` is the function name).
- Use a technical term only when the situation needs it, and then use it the same way every time. If a term is project-specific, define it once in GLOSSARY.md.
- Short sentences. One idea per sentence. Active voice.

## Keep it short

LLMs, ChatGPT especially, pad docs. Do not.

- Say each fact once, in one sentence or one bullet.
- Delete sentences that repeat the heading, the code, or the previous sentence.
- No intros ("This document describes..."), no outros or summaries, no transitions ("Moreover", "In conclusion"), no praise or marketing ("powerful", "seamless", "robust").
- No hedging ("typically", "generally", "might") unless the uncertainty is real and matters.
- Prefer bullets, tables, and signatures over paragraphs.
- Examples: only when the contract is unclear without one. Max one per concept, as short as possible.
- Do not describe what the code already shows. Write what a reader cannot get from the code: contracts, invariants, reasons, decisions, constraints, gotchas, how parts connect.
- Always keep: numbers, limits, names, paths, reasons for decisions, warnings.
- No changelogs, history, or "recently". Git has history.
- Size limits (checked by `lint`): 150 lines and 1200 words per doc. Over that, split by topic into new IDs.
- One fact lives in one place. Link by ID instead of copying.

## Maintaining docs

1. Code change that alters a contract, invariant, or gotcha -> update the doc in the same change and update `updated:`.
2. Edit in place with small diffs. Do not rewrite a whole file for a small change.
3. Before adding content, check INDEX.md for an existing doc on the topic. Extend it rather than creating a near-duplicate.
4. Wrong or obsolete content: delete it. Whole doc obsolete: set `status: deprecated` and add `replaced-by: ID`; delete it once nothing references it.
5. After any add, move, or delete: run `index`, then `lint`, and fix what it reports.

## Handing tasks to other agents

Reference docs by ID instead of pasting them:

```json
{"type":"refactor|feature|fix|test|docs","target":"src/auth/login.py:verify","spec":["AUTH-01#s2","AUTH-01#s3"],"done_when":"pytest tests/auth passes","notes":"optional, one line"}
```

The receiving agent loads only the referenced sections. If a referenced doc is missing or contradicts the code, fix or flag the doc before proceeding.

## Script

`scripts/docs_tool.py` in this skill folder. In a project the path is `.agents/skills/agent-docs/scripts/docs_tool.py` for every agent. Run it from the project root (default docs dir is `docs`). Do these by script, never by hand.

- `init [docs_dir]` adds frontmatter, doc ID, and `{#sN}` section IDs to md files without them. Moves the first `# Title` line into `title:`. Sets `summary: TODO`, `status: draft`, empty `code: []`. Then rebuilds the index.
- `new <relpath> "<title>" [docs_dir]` creates a stub doc with the next free ID.
- `index [docs_dir]` rebuilds INDEX.md (and area indexes above 40 docs) from frontmatter.
- `lint [docs_dir]` checks: missing or duplicate IDs, bad frontmatter (all fields required, `code: [...]`, ISO `updated`), empty or `TODO` summary, size limits, sections without IDs, `code:` paths that do not exist, broken `ID#sN` references, stale INDEX.md. Exit code 1 if anything is wrong.
- `show ID[#sN] [docs_dir]` prints only that doc or section.
- `find <words> [docs_dir]` prints index rows whose ID, path or summary hold all the words. Cheaper than reading an index.
- `stats [docs_dir]` prints words, lines, and a rough token estimate per doc. Run before and after condensing to see the saving.

## Migrating existing docs

Existing docs are often long and wordy. Migration means: add structure, translate to English, cut filler. It never means: add content.

Rules for the migrating agent:
- Do not add facts, examples, or explanations that are not in the source. If something is unclear, keep the original wording and list the doubt in your reply.
- Do not drop numbers, names, paths, limits, warnings, or reasons for decisions. Cutting those is the most common failure.
- When unsure if a sentence is filler, keep it and mention it in your reply.
- Keep code identifiers and quoted error messages exactly as in the source.

Steps:
1. Work in a git branch. Run `stats` and note the totals.
2. Run `init`. It gives every file an ID and section IDs. Do not touch the IDs.
3. Take 2-3 files first and condense them: translate to English, apply "Language and words" and "Keep it short", fill `summary` (one line) and `code:` (paths the doc covers; check they exist). A human reviews the diff before continuing.
4. Then continue in small batches, one file at a time. Do not process many files in one go; quality drops and content gets lost.
5. Split files over the size limits by topic with `new`, moving content (not copying). Merge or delete duplicates; keep one source of truth.
6. Put project-specific terms you had to keep into GLOSSARY.md and ask the user to confirm them.
7. Update old links and task templates to use IDs.
8. Run `index`, `lint`, `stats`. Fix everything `lint` reports. Report the before/after totals and a list of doubtful spots.
