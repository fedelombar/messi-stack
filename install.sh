#!/usr/bin/env bash
# Copy the messi-stack skills and agents into ~/.claude.
# Usage: ./install.sh [--force]
#   --force  replace skills and agents that already exist with the same name.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
force=no
[ "${1:-}" = "--force" ] && force=yes

mkdir -p "$dest/skills" "$dest/agents"
installed=0
skipped=()

for dir in "$here"/skills/*/; do
	name="$(basename "$dir")"
	target="$dest/skills/$name"
	if [ -e "$target" ] && [ "$force" = no ] && ! diff -rq "$dir" "$target" >/dev/null 2>&1; then
		skipped+=("skills/$name")
		continue
	fi
	rm -rf "$target"
	cp -R "$dir" "$target"
	installed=$((installed + 1))
done

for file in "$here"/agents/*.md; do
	name="$(basename "$file")"
	target="$dest/agents/$name"
	if [ -e "$target" ] && [ "$force" = no ] && ! diff -q "$file" "$target" >/dev/null 2>&1; then
		skipped+=("agents/$name")
		continue
	fi
	cp "$file" "$target"
	installed=$((installed + 1))
done

# reflect reads this file to find the clone, so that skill edits land in the source.
printf '%s\n' "$here" > "$dest/skills/messi-mode/SOURCE"

echo "Installed $installed items into $dest."
if [ "${#skipped[@]}" -gt 0 ]; then
	echo "Skipped, because a different version already exists:"
	printf '  %s\n' "${skipped[@]}"
	echo "Run ./install.sh --force to replace them."
fi
echo "Start a new Claude Code session, then type /messi-mode followed by your task."
