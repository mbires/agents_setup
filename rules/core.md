## Working rules
- If something needed for the task is unclear, ask the user. Do not guess.
- Never read generated or bulky folders: `.venv/`, `venv/`, `node_modules/`, `build/`, `dist/`, `__pycache__/`, caches, logs, data dumps. Find files by name or grep first; read only the part you need.
- Skills live in `.agents/skills/` (Claude Code: `.claude/skills/`, same content). Load a skill only when its task comes up.
