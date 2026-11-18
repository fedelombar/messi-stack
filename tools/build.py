#!/usr/bin/env python3
"""Build the messi-mode stack from a pinned pstack checkout plus the overlay.
Usage: build.py <pstack-dir> <overlay-dir> <out-dir>
Every replacement must match, so an upstream change fails the build loudly."""
import re, shutil, sys
from pathlib import Path

src, overlay, out = map(Path, sys.argv[1:4])
SKILLS = ["why","how","unslop","architect","interrogate","tdd","arena","swarm","reflect","correct",
          "no-comments","figure-it-out","benchmark-checklist","show-me-your-work","technical-writing","in-your-own-words",
          "blast-radius","typescript-best-practices","create-verification-skill","maintain-verification-skill","sharpen",
          "teach","recall","bro","ketchup","create-formal-verification-skill","maintain-formal-verification-skill","statechart"]
PLAYBOOKS = ["investigation","bug-fix","feature","refactoring","prototype","perf-issue","runtime-forensics",
             "trace-forensics","multi-phase-plan","autonomous-run","session-pickup","pause-safely","authoring-a-skill",
             "hillclimb","eval","visual-parity","babysit","worktree-cleanup"]
MODEL = re.compile(r" using your configured [a-z-]+ model \(default `claude-opus-5-5-xhigh-fast`\)")
POINTER = ("Skills named in bold live at `~/.claude/skills/<name>/SKILL.md`, and principles at "
           "`~/.claude/skills/messi-mode/principles/<name>.md`. Read the file and follow it. Do not call the Skill tool for it.\n")

def sub(text, old, new, where):
    if old not in text: sys.exit(f"build: no match in {where}: {old[:70]!r}")
    return text.replace(old, new)

EDITS = {
 "skills/how": [("Spawn one Task subagent with `subagent_type: generalPurpose` and `readonly: true` that",
                 "Spawn one `Agent` with `subagent_type: \"Explore\"` that")],
 "skills/interrogate": [
   ("Read the `interrogate reviewers` line in place of `arena runners`.",
    "Use the review panel from the Subagents section of the **messi-mode** skill."),
   ("Spawn each adversary as `generalPurpose`.", "Start each adversary the way its panel seat says, an `Agent` call or the Codex CLI command.")],
 "skills/arena": [
   (re.compile(r"3\. Pick the runners from the `arena runners` line.*?\n"),
    "3. Pick the runners from the panel in the Subagents section of the **messi-mode** skill. Keep at least two runners, and say so when a seat drops. Spawn more for multiple design directions, and repeat one seat when the work is generation-bound, not judgment-sensitive.\n"),
   ("Spawn all N subagents in one message with `run_in_background: true`, each", "Spawn all N agents in one message, each"),
   (re.compile(r"After all Phase B candidates complete, spawn one readonly judge.*?While you read"),
    "After all Phase B candidates complete, spawn one judge on the cross-judge seat from the Subagents section of the **messi-mode** skill. The judge is never from the session's vendor. With no other vendor available, skip the judge and say so. Tell the judge to edit no files. While you read")],
 "skills/swarm": [
   (re.compile(r"3\. Pick the worker model from the `swarm workers` line.*?\n"),
    "3. Pick the worker model per the Subagents section of the **messi-mode** skill. For a model race, name each arm's agent type up front.\n"),
   (re.compile(r"Spawn all N workers in one message with `subagent_type: generalPurpose`.*?\n\nWhen a worker must start from a non-default pushed branch, pass `cloud_base_branch`\.\n"),
    "Spawn all N workers in one message with `subagent_type: \"general-purpose\"`. A worker that writes gets `isolation: \"worktree\"`, and its brief names the branch or commit to check out.\n")],
 "skills/reflect": [
   ("Before approval, show its destination, `.cursor/skills/<skill>/` or `~/.cursor/skills/<skill>/`. After approval, copy the skill folder there and edit the copy. Never open a PR or push.",
    "Before approval, show its destination, `.claude/skills/<skill>/` in the repo or `~/.claude/skills/<skill>/`. After approval, edit the skill there, copying a plugin's skill folder there first. A repo skill is shared with the team, so its edit is a normal change on a branch. Never open a PR or push.\n\nA learning about the user or the project that is not a rule for a skill goes to the session's memory directory when the session has one, not into a skill.\n\nA messi-stack skill is built from a clone, and an edit to the installed copy is lost at the next install. When `~/.claude/skills/messi-mode/SOURCE` exists, it holds the path of that clone. Make the edit there: in `tools/overlay/` for a hand-written file, or as one replacement in `tools/build.py` for a file that comes from pstack. Then rebuild, run `tools/check.py`, copy the changed files into `~/.claude`, and commit in the clone. Do not push.")],
 "skills/no-comments": [
   ("Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.",
    "Use the caller's files or diff. Otherwise use the current diff against the repo's integration branch, including the working tree.\n\nWhen the repo has its own comment-style skill, read it first. It decides what stays. Pass its path to Comment Sicko as an added keep rule, and reject any kill that it protects."),
   ("Spawn `Task` with `subagent_type: \"comment-sicko\"`.", "Spawn `Agent` with `subagent_type: \"comment-sicko\"`.")],
 "skills/show-me-your-work": [
   ("Read this run's transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path). Don't glob across `~/.cursor/projects/*/`. That reads unrelated private chats.",
    "Read this run's transcript, the newest `.jsonl` directly under this workspace's folder in `~/.claude/projects/`. Don't read another workspace's folder. That reads unrelated private chats.")],
 "principles/never-block-on-the-human": [
   ("- Irreversible actions (force-push, delete production data, send external messages) still require confirmation.",
    "- The pause list in the Autonomy section of the **messi-mode** skill still requires confirmation: production changes, messages to people, outside writes nobody asked for, force-push, merges, deleted data, and a push or PR nobody asked for.")],
 "playbooks/bug-fix": [("Drive a long or stubborn hunt with Cursor's `/loop` command.", "Drive a long or stubborn hunt with the `/loop` skill."), (MODEL, "")],
 "playbooks/feature": [(MODEL, ""),
   (" Mandatory: no skip-with-reason escape, and Laziness Protocol does not override it (the gain is review separation, not lines saved). A subagent forbidden to spawn satisfies this by owning the diff directly with the same review separation.",
    " Skip the arena with a stated reason when one shape is plainly right.")],
 "playbooks/refactoring": [(MODEL, "")],
 "playbooks/perf-issue": [(MODEL, "")],
 "playbooks/autonomous-run": [
   ("Pick the wake mechanism using Cursor's `/loop` command (a built-in, not a pstack skill).", "Pick the wake mechanism using the `/loop` skill."),
   ("or use `AskQuestion`", "or use `AskUserQuestion`"),
   ("Surface only irreversible actions,", "Surface only the pause list in the Autonomy section of the **messi-mode** skill,")],
 "playbooks/session-pickup": [
   ("A local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path. Do not glob across `~/.cursor/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects), a cloud-agent URL, or a pushed branch.",
    "A local transcript (a `.jsonl` directly under this workspace's folder in `~/.claude/projects/`. Do not read another workspace's folder, that reads private chats from unrelated projects), a thread or session id the user gives you, or a pushed branch.")],
 "playbooks/authoring-a-skill": [
   ("1. Use the **create-skill** skill (Cursor's built-in for authoring SKILL.md files).",
    "1. Use the repo's or the session's skill-authoring skill when one is listed. Otherwise write the `SKILL.md` directly.")],
 "skills/recall": [
   ("Transcripts live at `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`, where `<slug>` is the workspace path with the leading slash dropped and each \"/\" turned into \"-\" (so `/Users/you/proj` becomes `Users-you-proj`). Every line is one chat message.",
    "Transcripts live at `~/.claude/projects/<slug>/<session-id>.jsonl`, where `<slug>` is the workspace path with every character that is not an ASCII letter or digit turned into \"-\" (so `/Users/you/proj` becomes `-Users-you-proj`). Every line is one event. Work done in a git worktree has its own slug, so include the folders for this repo's worktrees."),
   (" Turning habits into a durable skill is `automate-me`.", ""),
   (", in agent mode because readonly strips MCP access,", ", as `general-purpose` so it keeps the session's MCP tools,")],
 "skills/ketchup": [
   ("a chart or diagram from `/visualize`", "a chart or diagram from the session's chart or diagram tools"),
   ("a `/visualize` chart", "a chart from the session's chart tools")],
 "skills/create-formal-verification-skill": [("with the pstack [`/statechart`]", "with the [`/statechart`]")],
 "playbooks/hillclimb": [(MODEL, "")],
 "playbooks/eval": [
   (" An agent that only dispatches, polls, or packs results runs on `claude-opus-5-5-medium-fast`.", ""),
   ("Read each candidate's local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names this path). Do not glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.",
    "Read each candidate's transcript under this workspace's folder in `~/.claude/projects/`. Subagent transcripts sit in the session's `subagents/` folder. Do not read another workspace's folder. That reads private chats from unrelated projects.")],
 "playbooks/babysit": [
   (re.compile(r"- Use `gh` by default, or `origin pr`.*?\n"),
    "- Use `gh`. Status comes from `gh pr view <pr> --json mergeable,reviewDecision,statusCheckRollup` and `gh pr checks <pr>`. When the session has its own tool to watch a PR, wait with that instead of polling.\n"),
   ("Triage Bugbot skeptically", "Triage review-bot comments skeptically"),
   ("per `../references/bugbot-triage.md`", "per `~/.claude/skills/messi-mode/references/bot-review-triage.md`"),
   (" or `origin pr thread reply <thread-id> <pr> --body-file <reply-file>`", "")],
 "playbooks/worktree-cleanup": [
   ("then run `scripts/worktree-audit.sh", "then run `~/.claude/skills/messi-mode/scripts/worktree-audit.sh"),
   ("`.cursor/worktrees/myrepo/x`", "`.claude/worktrees/x`"),
   ("`~/Library/Application Support/Cursor` (`state.vscdb.backup`, and `snapshots/roots/<root>` where a `<root>` named for a folder you opened as a workspace balloons), ", "")],
 "references/bot-review-triage": [
   ("# Bugbot triage", "# Review-bot triage"),
   ("(`../playbooks/babysit.md`)", "(`~/.claude/skills/messi-mode/playbooks/babysit.md`)")],
 "scripts/worktree-audit": [
   ("# Transcripts dir: ~/.cursor/projects/<slugified-repo-path>/agent-transcripts.", "# Transcripts: every workspace folder under ~/.claude/projects, since each worktree has its own."),
   ('transcripts="$HOME/.cursor/projects/$slug/agent-transcripts"', 'transcripts="$HOME/.claude/projects"')],
 "agents/comment-sicko": [("feed me the current diff against `main`", "feed me the current diff against the repo's integration branch")],
}

def transform(key, text):
    for old, new in EDITS.get(key, []):
        if isinstance(old, re.Pattern):
            text, n = old.subn(lambda m: new, text)
            if n == 0: sys.exit(f"build: no regex match in {key}: {old.pattern[:70]!r}")
        else:
            text = sub(text, old, new, key)
    return text.replace("poteto-mode", "messi-mode").replace("poteto-agent", "messi-agent").replace(".cursor/skills/", ".claude/skills/")

def add_pointer(text):
    if not re.search(r"\*\*[a-z][a-z-]+\*\*", text): return text
    m = re.search(r"^# .*\n", text, flags=re.M)
    if m: return text[:m.end()] + "\n" + POINTER + text[m.end():]
    end = text.index("\n---\n", 4) + 5
    return text[:end] + "\n" + POINTER + text[end:]

if out.exists(): shutil.rmtree(out)
mm = out / "skills/messi-mode"
for s in SKILLS:
    shutil.copytree(src / "skills" / s, out / "skills" / s, ignore=shutil.ignore_patterns("test", "*.test.ts", "bun.lock"))
    f = out / "skills" / s / "SKILL.md"
    f.write_text(add_pointer(transform(f"skills/{s}", f.read_text())))
(mm / "principles").mkdir(parents=True); (mm / "playbooks").mkdir()
for d in sorted((src / "skills").glob("principle-*")):
    name = d.name.removeprefix("principle-")
    (mm / "principles" / f"{name}.md").write_text(transform(f"principles/{name}", (d / "SKILL.md").read_text()))
for p in PLAYBOOKS:
    (mm / "playbooks" / f"{p}.md").write_text(transform(f"playbooks/{p}", (src / "skills/poteto-mode/playbooks" / f"{p}.md").read_text()))
(out / "agents").mkdir()
(out / "agents/comment-sicko.md").write_text(add_pointer(transform("agents/comment-sicko", (src / "agents/comment-sicko.md").read_text())))
(mm / "references").mkdir(); (mm / "scripts").mkdir()
(mm / "references/bot-review-triage.md").write_text(transform("references/bot-review-triage", (src / "skills/poteto-mode/references/bugbot-triage.md").read_text()).replace("Bugbot", "review-bot"))
audit = mm / "scripts/worktree-audit.sh"
audit.write_text(transform("scripts/worktree-audit", (src / "skills/poteto-mode/scripts/worktree-audit.sh").read_text())); audit.chmod(0o755)
shutil.copy(src / "LICENSE", mm / "LICENSE")
shutil.copytree(overlay, out, dirs_exist_ok=True)
# Each playbook opens with an unconditional list of principle files to read.
# Measured upstream (cursor/plugins#726): this is what makes agents read them.
READ_FIRST = {
 "investigation": ["prove-it-works","attack-the-premise","guard-the-context-window"],
 "bug-fix": ["fix-root-causes","prove-it-works","attack-the-premise","laziness-protocol","sequence-verifiable-units"],
 "feature": ["foundational-thinking","model-the-domain","laziness-protocol","separate-before-serializing-shared-state","sequence-verifiable-units","prove-it-works"],
 "refactoring": ["model-the-domain","foundational-thinking","redesign-from-first-principles","subtract-before-you-add","laziness-protocol","migrate-callers-then-delete-legacy-apis","minimize-reader-load","prove-it-works","sequence-verifiable-units"],
 "prototype": ["exhaust-the-design-space"],
 "perf-issue": ["explain-the-number","sequence-verifiable-units","prove-it-works"],
 "hillclimb": ["explain-the-number","sequence-verifiable-units","guard-the-context-window"],
 "runtime-forensics": ["fix-root-causes","guard-the-context-window"],
 "trace-forensics": ["fix-root-causes","guard-the-context-window"],
 "visual-parity": ["prove-it-works"],
 "multi-phase-plan": ["sequence-verifiable-units","outcome-oriented-execution"],
 "autonomous-run": ["sequence-verifiable-units","prove-it-works","never-block-on-the-human"],
 "session-pickup": ["guard-the-context-window","prove-it-works"],
 "worktree-cleanup": ["build-the-lever","prove-it-works","guard-the-context-window"],
 "authoring-a-skill": ["encode-lessons-in-structure"],
 "opening-a-pr": ["sequence-verifiable-units"],
}
for name, plist in READ_FIRST.items():
    f = mm / "playbooks" / f"{name}.md"
    for pr in plist:
        if not (mm / "principles" / f"{pr}.md").exists(): sys.exit(f"build: {name} lists missing principle {pr}")
    text = f.read_text(); head, rest = text.split("\n", 1)
    line = "Before step 1, `Read` these files in `~/.claude/skills/messi-mode/principles/`: " + ", ".join(f"`{x}.md`" for x in plist) + ". Read them now, in full, not when you cite them."
    f.write_text(head + "\n\n" + line + "\n" + rest)
print("built", sum(1 for _ in out.rglob("*") if _.is_file()), "files")
