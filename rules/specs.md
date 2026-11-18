## Specifications
- Specs live in `specification/` and work like docs, with their own index. Always pass the folder to the script: `docs_tool.py show FEAT-07#s3 specification`.
- To write, edit, split, review or migrate a spec, use the `spec-writing` skill. This project's spec layout, gates and protected files are in `.agents/spec-writing.md`.
- `status`: `draft` = not approved, do not implement; `stable` = approved; `deprecated` = done or replaced, the contract is in `docs/`.
- When you implement a spec:
  - read the brief once in full, then work one numbered section at a time;
  - to check a fact again, load only that section with `show`, do not re-read the file;
  - reference the section ID in tests, code comments and commits (`FEAT-07#s3`);
  - if the spec contradicts the code, stop and report it, do not guess;
  - when the brief is done, set `status: deprecated`, then run `index` and `lint` on `specification`.
