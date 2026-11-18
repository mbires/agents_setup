## GUI rules (Qt)
- Every GUI job that runs off the GUI thread registers in the project's task registry, so it is visible and stopped on close. Contract: `<doc ID>`, enforced by `<test>`.
- Every button, checkbox and action has a short tooltip (`setToolTip`). Contract: `<doc ID>`, enforced by `<test>`.
