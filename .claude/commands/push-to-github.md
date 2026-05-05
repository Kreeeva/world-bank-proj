# Push to GitHub

Initialize git, create a remote repo, and push. The GitHub CLI (`gh`) is NOT installed on this machine — use `git` commands directly instead.

## Step 1 — Check git config
```powershell
git config --global user.name
git config --global user.email
```
If blank, set them:
```powershell
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Step 2 — Initialize and stage
```powershell
cd "C:\Users\oreva\Documents\world bank proj"
git init
git add .gitignore CLAUDE.md app.py worldbankproj.ipynb
git add data\ model\
```
Do NOT stage `venv\` — it is excluded by .gitignore.

## Step 3 — First commit
```powershell
git commit -m "Initial commit: Infrastructure Credit Risk Model"
```

## Step 4 — Create GitHub repo and push
The user must create the repo on GitHub first (github.com → New repository).
Then:
```powershell
git remote add origin https://github.com/<username>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Notes
- If `gh` is needed in future, install it: `winget install GitHub.cli`
- Never use `Bash` tool for git commands on this machine — use `PowerShell` tool only.
