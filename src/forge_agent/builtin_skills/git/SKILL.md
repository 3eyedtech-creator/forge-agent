---
name: git
description: Use when working with local Git repository state, diffs, branches, and commits.
---

# Git

When working with local Git:

1. Inspect repository state before making Git changes.
2. Prefer read-only commands first: `git status`, `git diff`, `git log`, and current branch.
3. Review changed files before staging or committing.
4. Keep commits focused and write clear commit messages.
5. Do not run destructive commands such as `git reset --hard`, `git clean`, force push, or rebase unless the user explicitly asks and approves.
6. Mention uncommitted or unrelated changes before making assumptions.
7. After Git operations, report what changed and what still needs review.
