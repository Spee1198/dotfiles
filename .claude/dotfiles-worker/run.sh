#!/bin/zsh
# Daily: turn logged corrections into rule and skill edits, applied locally.
set -euo pipefail
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

DOTFILES_GIT="$HOME/.dotfiles"
WORKER_DIR="$HOME/.claude/dotfiles-worker"
# Claude Code refuses writes under ~/.claude, so agent-written files live here.
DATA_DIR="$HOME/.local/share/dotfiles-worker"
INBOX="$DATA_DIR/inbox.md"
DIGEST="$DATA_DIR/digest.md"
COMMITS="$DATA_DIR/commits.txt"
WORKTREE="/tmp/dotfiles-worker"
AUTO_APPLY_PATHS='^[.](cursor/(rules|skills)|claude/skills)/'
MEMORY_DIR="$HOME/.claude/memory/rw-bess"
# Memory holds Redwood data, so it backs up to company OneDrive, never GitHub.
MEMORY_BACKUP_DIR="$HOME/Library/CloudStorage/OneDrive-RedwoodMaterials/AI Memory Backup/rw-bess"

dot() { git --git-dir="$DOTFILES_GIT" --work-tree="$HOME" "$@"; }
notify() { osascript -e "display notification \"$1\" with title \"dotfiles worker\""; }

back_up() {
  mkdir -p "$MEMORY_BACKUP_DIR" && rsync -a --delete "$MEMORY_DIR/" "$MEMORY_BACKUP_DIR/" \
    || notify "Memory backup to OneDrive failed. Is OneDrive running?"
  dot push -q origin main || notify "dot push failed. Run it by hand to see why."
}

cd "$HOME"
# Commit live edits first so the fast-forward below cannot collide with them.
dot add -u
# Memory and .orig copies hold Redwood data and stay local; see info/exclude.
dot add .cursor/rules .cursor/skills .claude/skills ':(exclude)*.orig-*'
dot diff --cached --quiet || dot commit -q -m "dotfiles: snapshot before worker run"
back_up

python3 "$WORKER_DIR/extract_feedback.py" > "$DIGEST"
[[ -s $INBOX || -s $DIGEST ]] || exit 0

branch="worker/$(date +%Y-%m-%d-%H%M)"
rm -rf "$WORKTREE"
dot worktree prune
dot worktree add -q -b "$branch" "$WORKTREE" main

: > "$COMMITS"
cd "$WORKTREE"
claude -p "$(cat "$WORKER_DIR/prompt.md")" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep" \
  --add-dir "$DATA_DIR"

# One commit per logged file, so dot revert can undo a single fix.
while IFS= read -r line; do
  [[ $line == *' | '* ]] || continue
  file=${line%% | *}
  [[ -n $(git status --porcelain -- "$file") ]] || continue
  git add -- "$file"
  git commit -q -m "${line#* | }" -- "$file"
done < "$COMMITS"
git add -A
git diff --cached --quiet || git commit -q -m "rules: worker edits with no logged message"
changed=$(git diff --name-status main..HEAD)

cd "$HOME"
dot worktree remove --force "$WORKTREE"
if [[ -z $changed ]]; then
  dot branch -q -D "$branch"
  exit 0
fi

needs_review=$(print -r -- "$changed" | awk -v ok="$AUTO_APPLY_PATHS" '$1 != "M" || $2 !~ ok')
if [[ -n $needs_review ]]; then
  notify "Held for review: dot diff main..$branch"
  exit 0
fi

count=$(dot rev-list --count "main..$branch")
dot merge -q --ff-only "$branch"
dot branch -q -d "$branch"
dot push -q origin main || notify "dot push failed. Run it by hand to see why."
notify "$count rule fixes applied. dot log -p to see them."
