# Git Commands – Pro Reference

## Repository Setup

### Create a new repository (on GitHub) and clone locally
```bash
# Option 1: Create with README, .gitignore, license (from GitHub web UI)
git clone https://github.com/yourname/repo.git

# Option 2: Create empty locally and push
mkdir myproject && cd myproject
git init
git remote add origin https://github.com/yourname/repo.git
# Create files, then
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Clone an existing repository
```bash
git clone <url> [folder-name]
```

## Basic Workflow

| Command | Purpose |
|---------|---------|
| `git status` | Show working tree status |
| `git add <file>` | Stage changes |
| `git add .` | Stage all changes |
| `git commit -m "message"` | Commit staged changes |
| `git push` | Push commits to remote |
| `git pull` | Fetch and merge remote changes |

## Branching & Merging

```bash
git branch <branch-name>          # Create branch
git checkout <branch-name>        # Switch branch
git checkout -b <branch-name>     # Create and switch
git merge <branch>                # Merge into current branch
git branch -d <branch>            # Delete local branch
git push origin --delete <branch> # Delete remote branch
```

## Undoing Changes

### Unstage a file (keep changes)
```bash
git reset HEAD <file>
```

### Discard local changes in a file (revert to last commit)
```bash
git checkout -- <file>
```

### Amend last commit (message or forgotten files)
```bash
git commit --amend -m "new message"
# If you forgot to add a file:
git add forgotten-file
git commit --amend --no-edit
```

## Resetting & Rewriting History

### Soft reset (keep changes staged)
```bash
git reset --soft HEAD~1   # Undo last commit, changes remain staged
```

### Mixed reset (default) – keep changes unstaged
```bash
git reset HEAD~1
```

### Hard reset (discard all changes)
```bash
git reset --hard HEAD~1
```

### Revert a commit (safe for shared branches)
```bash
git revert <commit-hash>
```

### Interactive rebase (rewrite multiple commits)
```bash
git rebase -i HEAD~3   # Squash, reword, etc.
```

## Working with Remote

### Show remotes
```bash
git remote -v
```

### Change remote URL
```bash
git remote set-url origin <new-url>
```

### Fetch all branches
```bash
git fetch --all
```

## Stashing

```bash
git stash                 # Save current changes
git stash list            # List stashes
git stash pop             # Apply last stash and remove from list
git stash apply           # Apply last stash without removing
git stash drop            # Remove last stash
```

## Log & History

```bash
git log --oneline --graph --all   # Pretty history
git reflog                         # Show all HEAD movements (useful for recovery)
```

## Tagging

```bash
git tag v1.0.0
git push origin v1.0.0
git tag -d v1.0.0                   # Delete local tag
git push origin --delete v1.0.0    # Delete remote tag
```

## Pro Tips

- Use `git add -p` to stage changes interactively.
- Set up aliases: `git config --global alias.co checkout`
- `git diff` to see unstaged changes; `git diff --staged` for staged changes.
- When you mess up and want to go back to a specific old commit:  
  `git checkout <commit-hash>` (detached HEAD) – then create a branch if needed.
