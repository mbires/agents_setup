## Subagents
- Simple, clearly bounded work (find files, read and summarize, mechanical edits such as renames or bulk replace) goes to the `quick-worker` subagent (small model).
- Work that needs judgment across several files (bug analysis, comparing options, review) goes to the `worker` subagent (mid model), or to `quick-worker` first and `worker` only if it failed.
- Design, architecture, specs and final review stay with you.
- This is not Local Coder delegation: subagents read and act in the real project; Local Coder writes code patches that you review and apply.
