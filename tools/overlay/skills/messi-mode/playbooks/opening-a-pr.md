### Opening a PR

Invoked at the end of every other playbook, when the user asked for a PR or told you to ship. Otherwise stop at local commits and offer the PR.

Work from a branch off the repo's integration branch, in a git worktree when other work is in the checkout, and keep unrelated work out of it. Rebase into small, landable commits. Run the `/simplify` skill over the diff before commit when the session lists it.

When the repo has a PR template or its own PR skill, that decides the title and body. Otherwise: title `type(scope): subject`, naming a real symbol when one carries the change. Body: a one-minute briefing under 40 lines with these `##` headings in order, dropping empty ones: `## Why`, `## What changed`, `## Scope`, `## Tradeoffs` (only rejected alternatives a reviewer would otherwise ask about), `## Blast Radius`, `## Verification`.

No `Co-Authored-By` trailer and no AI footer. Push with an explicit refspec, `git push origin <branch>:<branch>`. Check the base branch. Do not assume `main`.

Stack follow-ups by base branch. Open PRs ready with `gh pr create`, without `--draft`. Opening a PR does not start watching it and never authorizes a merge.
