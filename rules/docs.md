## Documentation
- Docs live in `docs/`. Find what you need with `docs_tool.py find <words>` or `docs/INDEX.md`, then load only those docs or sections (`show ID#sN`). Never read all docs.
- Script: `python .agents/skills/agent-docs/scripts/docs_tool.py` (`init`, `new`, `index`, `lint`, `show`, `find`, `stats`). Never invent or edit doc IDs.
- For any work on docs (write, edit, split, condense, translate, migrate, review), use the `agent-docs` skill.
- A code change that alters a contract, invariant or gotcha updates its doc in the same change. Then run `index` and `lint`.
- In hand-offs to other agents, reference docs by ID instead of pasting them.
