---
name: spec-writing
version: 1.1.0
description: Rules for writing, editing, splitting, reviewing and migrating specifications and task briefs (phases, features, fixes) that another agent will implement. Use whenever you write an implementation brief, plan a feature or fix for another agent, turn findings into a task, split a large spec, or migrate an old spec to the indexed format. Also trigger on "write a spec", "prepare a brief", "zadanie", "specifikácia". Not for implementing a spec; the project rules file covers reading one.
---

# Spec writing

A spec is a doc for an implementing agent. It follows the `agent-docs` skill in full: frontmatter, IDs, `{#sN}` sections, English, plain words, size limits, script. This skill adds only what is specific to specs.

1. **Load `agent-docs` first.** Do not repeat its rules here or in the spec.
2. **Read the project's spec rules in `.agents/spec-writing.md`** (called `project.md` below; one file for every agent, never inside a skill folder, so skill updates do not overwrite it). It holds this project's layout, ID prefixes, script call, `status` meaning, test gates, protected files and project rules. Where it differs from this file, `project.md` wins. If the project has none, create `.agents/spec-writing.md` from `templates/project.md` with the user before you write a spec.

## Who reads a spec, and how

The implementing agent reads the brief once top to bottom, then works one numbered section at a time. Later it reloads single sections with the script's `show ID#sN`. Write for that:

- Each `##` section stands on its own. Do not write "as above"; reference the section by ID (`FEAT-07#s2`).
- Facts live in one place: verified facts in "Current state" or a research doc, decisions in "Fixed decisions". Work sections reference them by ID and do not copy them.
- Each numbered work section is one unit of work that can be done, tested and committed alone.
- A feature split into several briefs has an overview that is the index of its briefs (`templates/overview.md`): ID, what, depends on, can run in parallel with, model.
- Size limit from `agent-docs` applies. Over it, split into briefs. Never ask for an exception.

## Content rules

- **No open questions for the implementer.** The spec settles research and decisions. Anything the implementer must decide is stated as such, with the options.
- **Checked facts.** Write when you checked code or a live site (`checked on YYYY-MM-DD`). Mark anything not checked as **unverified** and say how to check it first.
- **Real code.** Name paths, functions, classes and constants. Never "the crawler module".
- **User decisions apart.** Decisions the user must make go in "Decisions (approve or change)", never inside work steps. A spec with open user decisions is not ready to implement.
- **Scope.** Say what is out of scope and where it goes instead (another spec ID, or "later").
- **Personal data.** If a source holds personal data, say what is read and what is never stored.
- **Project rules.** Name every project rule from `project.md` that the change touches, by doc ID. Say "migration needed" or "no migration" for any schema change.
- **Delegation.** The `Model:` line follows the Local Coder "never delegate" list. Concurrency, migrations, auth, crypto and spec changes are always strong only.
- **No history.** No "previously", no changelog. Git has history.
- `code:` in frontmatter lists only paths that exist now. Files the spec creates are named in the body; `lint` fails on missing paths.

## Required parts of a brief

Start from `templates/brief.md`. Header lines, before the first `##`:
- `Model:` strong only, or which sections may go to Local Coder.
- `Depends on:` spec IDs that must be done first, and what may run in parallel. `nothing` if none.
- `Read first:` doc IDs (`ID` or `ID#sN`). Never paste doc text.

Sections, in this order. Leave out the ones that do not apply. `project.md` may add sections.

| Section | Content |
|---|---|
| Goal | What is true when this is done. Bullets. |
| Current state | Facts from the code, with the check date. For a fix: Problem, then Root cause. |
| Fixed decisions | Settled choices and the reason for each. |
| Decisions (approve or change) | Only until the user decides. Options and your recommendation. |
| Scope / Out of scope | Lists. |
| 1..N work sections | One unit of work each. Paths, names, behavior, limits. |
| Tests | Concrete cases, then the gates from `project.md`. |
| Docs | Doc IDs and sections to update, then `index` and `lint`. |
| Done when | Checkable criteria. One real run where possible. |

## Review checklist

Before you hand a spec to the user:
- [ ] `lint` passes for the files you touched.
- [ ] Header has `Model`, `Depends on`, `Read first`.
- [ ] No step needs research or a decision the spec does not settle.
- [ ] Every fact is dated or marked **unverified**.
- [ ] Every referenced doc ID exists (`show <ID>`). If specs and docs have separate indexes, `lint` does not check refs between them.
- [ ] Tests, Docs and Done when are present and checkable.
- [ ] Open user decisions are listed, and `status` says the spec is not approved yet.
- [ ] No protected file from `project.md` was touched.

## Migrating an old spec

Follow "Migrating existing docs" in `agent-docs`, plus the migration notes in `project.md`.
- Large old specs are split into briefs with an overview, not cut down to fit.
- A spec that is already implemented is not condensed. Check that its contracts are in the docs and list the gaps for the user.

## Script gotchas

- The script finds `{#sN}` only on `##` lines. `###` headings have no ID and cannot be loaded with `show`.
- `new` writes a `## Purpose {#s1}` stub. Replace the body with the template; keep the frontmatter the script wrote.
- `init` adds frontmatter to every md file without it in the folder. Check `project.md` for protected files before you run it.
