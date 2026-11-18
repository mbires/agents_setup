# <Project>: spec rules for this project

Save in the project as `.agents/spec-writing.md` (one copy for all agents). Defaults below are the standard layout from `_Claude`; change only what differs.

## Layout and IDs

```
specification/
  INDEX.md              # generated; read first
  phase/<name>.md       # PHASE-NN, roadmap phases
  feat/<name>.md        # FEAT-NN, single-file features
  feat/<feature>/       # large feature: 00_OVERVIEW.md + 01_<NAME>.md ... + RESEARCH.md
  fix/<name>.md         # FIX-NN, bug fixes
```

- Specs have their own index, separate from `docs/`. The first folder under `specification/` sets the ID prefix. Never put a spec directly in `specification/`.
- Script: `python .agents/skills/agent-docs/scripts/docs_tool.py <command> ... specification`. Without the folder it works on `docs/`.
- `lint` does not check refs between `docs/` and `specification/`; check them with `show <ID>` or `show <ID> specification`.

## Status

| `status` | Meaning |
|---|---|
| `draft` | Waiting for the user's approval. Do not implement. |
| `stable` | Approved. Ready or in progress. |
| `deprecated` | Implemented or replaced (`replaced-by: ID`). The contract now lives in `docs/`. |

Only the user moves a spec from `draft` to `stable`.

## Protected files

- <file>: read-only. Never run `init` on a folder that holds it.

## Test gates

```bash
<commands>
```

## Project rules a spec must name when touched

- <rule> → `<doc ID>`.

## Migration notes

- <how old specs are handled>
