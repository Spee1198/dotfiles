#!/bin/zsh
# Install these dotfiles into $HOME. Pass --shared on a laptop that is not yours.
set -euo pipefail

REPO="Spee1198/dotfiles"
GIT_DIR="$HOME/.dotfiles"
BACKUP_DIR="$HOME/.dotfiles-preexisting"
INSTALLED_LIST="$GIT_DIR/installed-files"
# settings.json lists directories by full path, written on this home.
ORIGINAL_HOME="/Users/spencer.green"
SETTINGS="$HOME/.claude/settings.json"
# Never-ask permissions, the open sandbox, and the daily worker stay on Spencer's own laptop.
SHARED_SKIP_PREFIXES=(.cursor/permissions.json .cursor/sandbox.json .cursor/cli-config.json Library/ .claude/dotfiles-worker/)

dot() { git --git-dir="$GIT_DIR" --work-tree="$HOME" "$@"; }

is_skipped() {
  local path="$1" prefix
  for prefix in "${SHARED_SKIP_PREFIXES[@]}"; do
    [[ "$path" == "$prefix"* ]] && return 0
  done
  return 1
}

is_shared=false
[[ "${1:-}" == "--shared" ]] && is_shared=true

if [[ -e "$GIT_DIR" ]]; then
  echo "$GIT_DIR already exists. Run ~/.dotfiles-bin/teardown.sh first." >&2
  exit 1
fi
command -v gh >/dev/null || { echo "Install the GitHub CLI (gh) and run gh auth login first." >&2; exit 1; }

gh repo clone "$REPO" "$GIT_DIR" -- --bare -q
dot config status.showUntrackedFiles no
dot reset -q

: > "$INSTALLED_LIST"
dot ls-files | while read -r file; do
  if $is_shared && is_skipped "$file"; then
    dot update-index --skip-worktree -- "$file"
    continue
  fi
  # Move aside anything already there; teardown puts it back.
  if [[ -e "$HOME/$file" || -L "$HOME/$file" ]]; then
    mkdir -p "$BACKUP_DIR/${file:h}"
    mv "$HOME/$file" "$BACKUP_DIR/$file"
  fi
  dot checkout -q -- "$file"
  echo "$file" >> "$INSTALLED_LIST"
done

if [[ "$HOME" != "$ORIGINAL_HOME" && -f "$SETTINGS" ]]; then
  sed -i '' "s|$ORIGINAL_HOME/|$HOME/|g" "$SETTINGS"
fi

"$HOME/.claude/sync-cursor-rules.sh"
echo "Installed $(wc -l < "$INSTALLED_LIST" | tr -d ' ') files. Shared mode: $is_shared."
$is_shared && echo "Run ~/.dotfiles-bin/teardown.sh before you hand the laptop back."
exit 0
