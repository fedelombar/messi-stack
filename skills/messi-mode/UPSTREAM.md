# Upstream

messi-mode and the skills it routes to are adapted from pstack by poteto, MIT licensed. See `LICENSE` in this folder.

- Source: https://github.com/cursor/plugins, folder `pstack/`
- Commit: `93b916d4a1e806507e22f4716b352fa91f2b227e`
- Copied on: 2026-11-17

## What came from pstack

- `messi-mode/principles/`: all 24 `principle-*` skills, one file each.
- `messi-mode/playbooks/`: 18 of the 22 playbooks, plus a rewritten Opening a PR.
- `messi-mode/references/bot-review-triage.md` (from bugbot-triage) and `messi-mode/scripts/worktree-audit.sh`.
- 28 skills in `~/.claude/skills/`: why, how, unslop, architect, interrogate, tdd, arena, swarm, reflect, correct, no-comments, figure-it-out, benchmark-checklist, show-me-your-work, technical-writing, in-your-own-words, blast-radius, typescript-best-practices, create-verification-skill, maintain-verification-skill, create-formal-verification-skill, maintain-formal-verification-skill, statechart, sharpen, teach, recall, bro, ketchup.
- `~/.claude/agents/comment-sicko.md`.

## What changed

Written new, from the pstack originals:

- `SKILL.md` (from poteto-mode). Cursor model slugs and the model rule file are gone. Code-writing delegates run on Opus, or on Fable when the user names it or the session runs on it. Autonomy pauses for production, messages to people, unrequested outside writes, pushes and PRs. Panels use Claude (Opus) plus GPT seats run through `codex exec`. The `ocx-*` agent types are not used: without the opencodex proxy they run on Claude. Added: the repo's own skills win, git rules, reply in the user's language.
- `worker.md` and `~/.claude/agents/messi-agent.md` (from worker.md and poteto-agent). Same changes, plus the git rules, because subagents see no memory.
- `playbooks/opening-a-pr.md`. A PR only when asked, the repo's PR template wins, `/simplify` in place of `/deslop`.

Edited in place. Every edit is a replacement in `tools/build.py`, which fails when upstream text no longer matches:

- Cursor tool names became Claude Code names: `Task` to `Agent`, `generalPurpose` to `general-purpose`, `readonly` to the `Explore` agent, cloud workers to `isolation: "worktree"`, `AskQuestion` to `AskUserQuestion`, transcript paths to `~/.claude/projects/`.
- Model lines in arena, swarm, interrogate and the code playbooks point at the Subagents section of messi-mode.
- Feature playbook: the arena step can be skipped with a stated reason.
- no-comments: the repo's comment-style skill decides what stays.
- reflect: project and user learnings go to memory, not into a skill.
- Removed references to things not copied: create-skill, cursor-team-kit, automate-me, `/visualize`, Origin's CLI.
- Babysit: status from `gh`, review-bot triage in place of Bugbot triage.
- recall, eval, session-pickup, worktree-audit.sh: transcripts under `~/.claude/projects/`.
- Each skill that names another skill got one line saying where skills and principles live.
- Each playbook opens with an unconditional list of principle files to read, and messi-mode makes reading the playbook the first step. cursor/plugins#726 measured this: 0 of 72 runs read a principle as shipped, 68 of 72 with the list in the playbook.
- From cursor/plugins#864: the todolist falls back to a file, delegates list steps they could not run under `Returned to parent`, and messi-mode is re-read after a compaction.
- From cursor/plugins#1155: the transcript slug replaces every character that is not an ASCII letter or digit.
- Small tasks skip the playbook.

## Not copied

- Playbooks shipping, autopilot-full and autopilot-stack. They merge PRs unattended and lean on Cursor cloud agents. messi-mode never merges without asking.
- setup-pstack. The Subagents section of messi-mode holds the model rules.
- poteto-help. It is a guide to pstack itself.
- automate-me. It mines Cursor transcripts and writes through Cursor's skill builder.
- make-bot-ui and ketchup-video. They need Grok Bot and a video pipeline.
- The `watch-pr` script. Babysit uses `gh` and the session's own PR watch tool.
- statechart's test corpus.

## Updating

The build script and the hand-written files live in the messi-stack repository, under `tools/`. From a clone of that repository:

```sh
git clone --depth 1 https://github.com/cursor/plugins /tmp/cursor-plugins
python3 tools/build.py /tmp/cursor-plugins/pstack tools/overlay out
python3 tools/check.py out
```

The build fails when upstream changed a passage that an edit depends on, and it names the file. Diff `out/` against `skills/` and `agents/` before you copy anything.
