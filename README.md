# _Claude kit

One source of truth for agent rules, skills and project setup across all projects. Goal: fewer tokens per session, no drifting copies.

## Layout

```
rules/        rule modules pasted into a project's AGENTS.md (core, subagents, docs, specs, local-coder, protected-files, gui-qt)
skills/       agent-docs, spec-writing, local-coder-delegation (installed into projects), project-setup (used from here only)
agents/       Claude Code subagents: quick-worker (Haiku), worker (Sonnet)
project/      skeleton for new projects: AGENTS.md stub, CLAUDE.md (@AGENTS.md), .claude/settings.json, .gitignore, docs/
local-coder/  Local Coder MCP registration (Claude, Codex/Antigravity) and global config example
scripts/kit.py
dist/         generated .skill zips (not in git)
```

## Use

New project:
```bash
python D:/_Dev/_Claude/scripts/kit.py new D:/_Dev/<Name>
```
Then open it with an agent. AGENTS.md says "SETUP PENDING", so the agent runs `project-setup`: it asks you questions, picks modules and skills, and writes the real AGENTS.md.

Existing project: ask the agent to "set up this project with the _Claude kit" (`project-setup`, section Migration).

Keep projects in sync:
```bash
python D:/_Dev/_Claude/scripts/kit.py check D:/_Dev/<Name>
python D:/_Dev/_Claude/scripts/kit.py update D:/_Dev/<Name>
```

Skills for the Claude app (claude.ai): `python scripts/kit.py pack`, then upload `dist/<name>.skill`.

## Rules for this repo

- Change rules and skills here, never in a project copy. Then bump `version:` in the skill's SKILL.md and run `kit.py update` per project.
- Each project has one rules file, `AGENTS.md`. `CLAUDE.md` only holds `@AGENTS.md`.
- Skills are copied to `.claude/skills/` (Claude Code) and `.agents/skills/` (Codex, Antigravity). Project-specific skill data lives outside skill folders (`.agents/spec-writing.md`), so updates never overwrite it.
- Rule modules stay generic: no project paths or IDs. Project details go under `## Project rules` in the project's AGENTS.md.
- Keep always-loaded text small: a module states when to use a skill; the skill holds the details.
