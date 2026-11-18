---
name: project-setup
version: 1.1.0
description: Set up a new project, or move an existing one, onto the shared _Claude kit (D:/_Dev/_Claude) - interview the user, pick rule modules and skills, write AGENTS.md, spec rules, settings and Local Coder config. Use when AGENTS.md says "SETUP PENDING", or when the user asks to set up, standardize or migrate a project's agent rules and skills.
---

# Project setup

Goal: the smallest set of rules and skills that lets agents work well in this project. Every always-loaded line costs tokens in every session, so add only what this project needs.

Kit layout (`KIT` = the folder that holds this skill's `skills/` folder, normally `D:/_Dev/_Claude`):
- `rules/*.md`: rule modules, pasted into AGENTS.md as they are.
- `skills/<name>/`: skills, installed with `python KIT/scripts/kit.py add <project> <name>`.
- `agents/*.md`: Claude Code subagents (`quick-worker` = Haiku, `worker` = Sonnet), installed with `kit.py add <project> agents`.
- `project/`: skeleton that `kit.py new` copies. `local-coder/`: MCP registration and global config example.

## 1. Interview first

Ask the user before you write anything. Ask in one message, only what you cannot find in the repo (README, pyproject, package.json, existing rules). Skip questions the user already answered.

1. What is the project, in 1-2 sentences? Main language and stack?
2. Size: small tool, or a long project with phases? (Decides specs and spec-writing.)
3. Which agents will work here: Claude Code, Codex, Antigravity/Gemini?
4. Local Coder delegation: yes or no? (Only for code with tests, usually Python.)
5. GUI? Which toolkit? Any GUI rules that tests enforce?
6. Files that agents must never change (roadmap, contracts, generated data)?
7. Test and lint commands (the gates)?
8. Folders that are large or private (data, exports, dumps) and must not be read?
9. Project rules that are not obvious from the code (external sources, rate limits, approvals needed for push or live runs, personal data)?
10. Git: remote repository to connect? (You never push without the user's approval.)

If an answer opens a new question that changes the setup, ask it. Never fill gaps with guesses; write `TODO(user)` and list it in your final reply.

## 2. Pick modules and skills

| Need | Rule module | Skill |
|---|---|---|
| always | `core.md` | - |
| Claude Code used | `subagents.md` | `agents` |
| any docs (almost always) | `docs.md` | `agent-docs` |
| specs / phased work | `specs.md` | `spec-writing` |
| Local Coder | `local-coder.md` | `local-coder-delegation` |
| protected files | `protected-files.md` (fill the paths) | - |
| Qt GUI | `gui-qt.md` (fill IDs and tests) | - |

Install: `python KIT/scripts/kit.py add <project> agent-docs spec-writing ... agents`. It copies each skill to `.claude/skills/` and `.agents/skills/`. Never edit those copies; change the kit and run `kit.py update`.

## 3. Write the files

- **AGENTS.md** (the only rules file): `# <Project>`, one line on what it is and the stack, then the chosen modules in the order of the table, then `## Project rules` with only what is specific to this project (answers 6-9). Paste modules verbatim; do not reword them, so `kit.py` and later updates stay simple. No rules that repeat a skill. Target under 1200 tokens.
- **CLAUDE.md** stays `@AGENTS.md`. Codex and Antigravity read AGENTS.md and `.agents/skills/` directly; no GEMINI.md needed. Antigravity also loads every file in `.agents/rules/`, so never keep rules there that AGENTS.md already has.
- **Spec rules** (if `spec-writing`): `.agents/spec-writing.md` from `KIT/skills/spec-writing/templates/project.md`. Keep the standard layout unless the user wants another; fill gates, protected files, project rules by doc ID.
- **`.claude/settings.json`**: add the user's large or private folders to `permissions.deny` as `Read(./<folder>/**)`. Keep the defaults.
- **`.gitignore`**: add the same folders if they should not be in git.
- **Local Coder** (if used): keep an existing `.mcp.json`; otherwise copy `KIT/local-coder/claude.mcp.json` to `.mcp.json` and `KIT/local-coder/agents.mcp_config.json` to `.agents/mcp_config.json`. The project path must be in `[security] allowed_roots` of `%APPDATA%/LocalCoderMCP/config.toml`; show the user the line to add and add it only after they say yes.
- **Docs**: run `python .agents/skills/agent-docs/scripts/docs_tool.py index`, and `... index specification` if specs are used.
- **Git**: add the remote only if the user gave one. Commit only when the user asks.

## 4. Existing project (migration)

Same steps, plus:
- Read the current CLAUDE.md, AGENTS.md and `.agents/rules/*`. Sort every rule into: covered by a kit module (drop it, use the module), project-specific (keep under `## Project rules`), outdated (list it and ask). Show the user this sorting before you write.
- Move `.claude|.agents/skills/spec-writing/project.md` to `.agents/spec-writing.md`, then remove the old skill copies and run `kit.py add` for the kit versions.
- Remove rule files that the new AGENTS.md replaces (for example `.agents/rules/local-coder.md`) only after the user agrees.
- If a project copy of a skill has changes that are worth keeping, tell the user; they go into the kit, not the project.
- Project copies of `docs_tool.py` (for example `scripts/docs_tool.py`) can hold fixes: compare them with the kit first and move useful changes into the kit before you delete them. Update paths in README and docs to `.agents/skills/agent-docs/scripts/docs_tool.py`.
- A doc system that differs from `agent-docs` (other statuses, Obsidian fields, own script) stays as it is: keep its rules under `## Project rules` and do not install `agent-docs`.

## 5. Finish

- Remove the `SETUP PENDING` line from AGENTS.md.
- Run `python KIT/scripts/kit.py check <project>`; everything must be `ok`.
- Reply with: modules and skills chosen, AGENTS.md size in tokens (characters / 4), every `TODO(user)`, and steps the user must do (plugins to disable, Local Coder config, remote).
