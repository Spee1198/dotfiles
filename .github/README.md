# dotfiles

Claude Code and Cursor rules, skills, hooks, and settings.
Tracked as a bare repo with `$HOME` as the work tree.

## Shared or borrowed laptop

```zsh
gh auth login
gh api repos/Spee1198/dotfiles/contents/.dotfiles-bin/setup.sh \
  -H 'Accept: application/vnd.github.raw' > /tmp/dotfiles-setup.sh
zsh /tmp/dotfiles-setup.sh --shared
```

`--shared` leaves out the never-ask permissions, the open sandbox, and the daily worker.
Before handing the laptop back:

```zsh
~/.dotfiles-bin/teardown.sh
```

## Own laptop

Same as above without `--shared`. Then add to `~/.zshrc`:

```zsh
alias dot='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'
```

Commit and back up with `dot add -u && dot commit -m "..." && dot push`.
