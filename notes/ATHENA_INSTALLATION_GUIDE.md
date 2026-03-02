# Contributing

Thank you for your interest in contributing to Project Athena!

## Before You Open an Issue

> **Ask Athena first.** That's what it's built for.

Most questions, troubleshooting, and "how do I..." queries can be answered by your own Athena agent. Try asking it directly:

- *"How do I get a Gemini API key?"*
- *"How do I write a protocol?"*
- *"How do I set up Supabase?"*
- *"I'm getting [error]. Can you help me fix it?"*

If Athena can't answer, *then* open an issue. See [SUPPORT.md](SUPPORT.md) for the full self-service flow.

## How to Contribute

### 1. Submit a PR (Preferred)

Don't just report it — **fix it**. We actively welcome pull requests:

1. Fork the repo
2. Let your Athena agent help you implement the change
3. Test your changes locally
4. Submit a PR with a clear description of what and why

We'll review and merge if it fits the project direction.

### 2. Share Your Workflows

Built a useful workflow? Submit a PR with:

- Your workflow file in `examples/workflows/`
- A brief description of what it does

### 3. Improve Documentation

Found something unclear? Help make it better:

- Fix typos or clarify explanations
- Add examples where helpful

### 4. Add Templates

Created a useful template? Share it:

- Add to `examples/templates/`
- Include usage instructions

### 5. Agent-Assisted Contributions

Let your Athena agent help you contribute! Using [Protocol 408](examples/protocols/workflow/408-autonomous-contribution-engine.md):

1. **Ask a question**: "Does Athena support X?"
2. **Agent verifies**: Searches codebase to confirm it's a gap
3. **Agent drafts**: Creates a structured RFC using templates
4. **You submit**: One-click GitHub Issue submission

Use the [Agent-Assisted Contribution](.github/ISSUE_TEMPLATE/agent_contribution.md) issue template for submissions.

## Guidelines

- Keep files modular (< 500 lines)
- Use clear, descriptive names
- Include comments where helpful
- Test your changes before submitting
- One PR = one topic (don't bundle unrelated changes)

## Code of Conduct

Be respectful. Be helpful. We're all learning together.

---

# PR Description Template

## Description

Brief description of what this PR does.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [x] Documentation update
- [ ] Workflow/template addition
- [ ] Other (please describe)

## Checklist

- [x] I have read the [CONTRIBUTING](../CONTRIBUTING.md) guidelines
- [x] My code follows the project's style (modular, <500 lines per file)
- [x] I have tested my changes
- [x] I have updated relevant documentation (if applicable)

## Related Issues

Closes #(issue number)

---

# Athena Installation Journey: Lessons Learned for Windows/PowerShell Users

> **Purpose:** Document the real-world experience of installing Athena in an existing private project by using a forked repo, including all errors, workarounds, and findings. This can help improve the onboarding experience for future Windows users.

> **Author:** Community Contributor  
> **Date:** 2026-02-25  
> **Athena Version:** 9.2.6 (GitHub repo)  
> **IDE:** VS Code + Kilo Code  
> **OS:** Windows 11 (PowerShell)

---

## Executive Summary

Successfully installed Athena in an existing private project after encountering multiple issues with the documented installation methods. The key finding: **the pip package (`athena-ai` v0.0.12) is NOT the same as the GitHub repo (`athena-sdk` v9.2.6)** and lacks the CLI commands documented in the README.

---

## The Documented Method (What Was Supposed to Work)

From the maintainer's instructions:

```powershell
pip install athena-ai
athena init --here --ide kilocode
```

### What Actually Happened

| Step | Expected | Actual |
|------|----------|--------|
| `pip install athena-ai` | Installs Athena | Installs v0.0.12 (old package) |
| `athena init --here --ide kilocode` | Initializes workspace | Error: `--here` option doesn't exist |
| `athena --help` | Shows all commands | Only shows `--log-level` and `--help` |

---

## Key Finding: Multiple Athena Packages Exist

### Package Comparison Table

| Package Name | Version | Source | Has `init`? | Has `--here`? | Has `--ide`? |
|--------------|---------|--------|-------------|---------------|--------------|
| `athena-ai` | 0.0.12 | PyPI | **NO** | **NO** | **NO** |
| `athena-sdk` | 0.0.1 | PyPI | Unknown | Unknown | Unknown |
| `athena-sdk` | 9.2.6 | GitHub repo | **YES** | **YES** | **YES** |

### Evidence

```powershell
# pip package (athena-ai v0.0.12)
PS C:\project> uv pip show athena-ai
Name: athena-ai
Version: 0.0.12
Location: C:\project\.venv\Lib\site-packages

PS C:\project> uv run athena --help
Usage: athena [OPTIONS]
Options:
  --log-level TEXT  Set logging level
  --help            Show this message and exit.
# NOTE: No init command! No --here option!

# GitHub repo (athena-sdk v9.2.6)
PS C:\athena-workspace> uv sync
Installed athena-sdk==9.2.6 (from file:///C:/athena-workspace)

# But even this version doesn't create a working 'athena' command!
PS C:\athena-workspace> athena --help
athena: The term 'athena' is not recognized...
```

---

## The Missing Entry Point Issue

The GitHub repo (`athena-sdk` v9.2.6) has the full CLI code in `src/athena/__main__.py`, but the `pyproject.toml` is missing the console script entry point.

### What's in the Code

```python
# src/athena/__main__.py (lines 104-125)
init_parser = subparsers.add_parser("init", help="Initialize a new Athena workspace")
init_parser.add_argument("target", nargs="?", type=Path, default=None)
init_parser.add_argument("--here", action="store_true")
init_parser.add_argument("--ide", "-i", 
    choices=["antigravity", "cursor", "vscode", "gemini", "kilocode", "roocode"])
```

### What's Missing from pyproject.toml

```toml
# This section should be added:
[project.scripts]
athena = "athena.__main__:main"
```

---

## The Working Solution: "Fork and Break" Workflow

### Background: Privacy First

Forking a public repo on GitHub creates a **public fork by default** - this means any private data you add would be visible to the world. To avoid this, we use a "fork and break" strategy to create a disconnected private copy.

### Step-by-Step "Fork and Break" Process

```powershell
# 1. Clone the public repo locally
cd C:\
git clone https://github.com/winstonkoh87/Athena-Public.git athena-workspace
cd athena-workspace

# 2. BREAK the fork connection (PowerShell syntax!)
Remove-Item -Recurse -Force .git

# 3. Initialize a fresh private git history
git init
git add .
git commit -m "Initial Athena setup for YOUR-PROJECT project"

# 4. Create a new private repo on GitHub
#    Go to: https://github.com → + → New repository → Private

# 5. Connect your local copy to GitHub
git remote add origin https://github.com/YOUR-USERNAME/athena-workspace.git
git branch -M main

# 6. Fix email privacy issue
git config --global user.email "YOUR-NOREPLY-EMAIL@users.noreply.github.com"
git config --global user.name "Your Name"
git commit --amend --reset-author --no-edit

# 7. Push to your private repo
git push -u origin main

# 8. Keep track of upstream changes (optional but recommended)
git remote add upstream https://github.com/winstonkoh87/Athena-Public.git

# 9. Install dependencies
uv sync

# 10. Run Athena from your project folder
cd C:\your-project
python -m athena init --here --ide kilocode
```

### What Finally Worked

```powershell
PS C:\your-project> python -m athena init --here --ide kilocode
# SUCCESS! Created:
#    .agent/workflows/
#    .framework/modules/
#    .context/memories/session_logs/
#    .kilocode/rules/athena.md
#    .athena_root
```

---

## PowerShell-Specific Issues

### The `rm -rf` Problem

The README mentions deleting the `.git` folder for private installations. On Windows PowerShell:

| Command | Works in PowerShell? |
|---------|---------------------|
| `rm -rf .git` | **NO** - "parameter not found" |
| `rmdir /s /q .git` | **NO** - "positional parameter not found" |
| `Remove-Item -Recurse -Force .git` | **YES** |

### The PATH Problem

```powershell
PS C:\project> pip install athena-ai
WARNING: The scripts pip.exe, pip3.12.exe and pip3.exe are installed in 
'C:\Users\USER\AppData\Roaming\Python\Python312\Scripts' which is not on PATH.
```

**Workaround:** Use `python -m pip` instead of just `pip`, or add the Scripts folder to PATH.

---

## Syncing with Upstream Athena-Public Project

### Understanding Your Three-Remote Setup

Your workspace has THREE remotes configured. This is the key to managing both your private work AND contributing to the project:

| Remote | GitHub Repo | Purpose |
|--------|-------------|---------|
| `origin` | YOUR-private-repo (private) | Your personal work + backups |
| `public` | YOUR-fork (public) | For submitting PRs to original |
| `upstream` | winstonkoh87/Athena-Public | Receiving updates from original |

```powershell
# Your remote setup (verify with):
git remote -v
# Should show:
# origin    https://github.com/YOUR-USERNAME/YOUR-private-repo.git (fetch)
# origin    https://github.com/YOUR-USERNAME/YOUR-private-repo.git (push)
# public   https://github.com/YOUR-USERNAME/Athena-Public.git (fetch)
# public   https://github.com/YOUR-USERNAME/Athena-Public.git (push)
# upstream https://github.com/winstonkoh87/Athena-Public.git (fetch)
# upstream https://github.com/winstonkoh87/Athena-Public.git (push)
```

### Setting Up The Three Remotes

If you haven't set this up yet:

```powershell
cd C:\athena-workspace

# Already have origin? Skip to adding others
git remote -v

# Add your public fork (for PRs)
git remote add public https://github.com/YOUR-USERNAME/Athena-Public.git

# Add the original repo (for updates)
git remote add upstream https://github.com/winstonkoh87/Athena-Public.git
```

### Scenario 1: Keeping Your Private Athena Repo Updated (Development)

Your workspace contains your private modifications and should be kept in sync with the upstream Athena-Public repo to get the latest features and bug fixes.

```powershell
cd C:\athena-workspace

# Check current remote configuration
git remote -v

# Fetch latest changes from upstream
git fetch upstream

# See what's new
git log upstream/main --oneline -10

# Merge into your private main branch
git merge upstream/main

# ⚠️ IMPORTANT: If you get "unrelated histories" error:
# This happens if you used "Fork and Break" (deleted .git and re-initialized)
# The solution is to allow merging unrelated histories ONCE:
git merge upstream/main --allow-unrelated-histories

# After merging, push to BOTH your forks
git push origin main      # Updates YOUR-private-repo (private)
git push public main     # Updates Athena-Public (public)

# Re-sync dependencies in your PROJECT project
cd C:\YOUR-PROJECT
uv sync
```

### Scenario 2: Contributing to Athena-Public (Public PR Fork)

If you want to contribute to Athena-Public, you use your public fork. Here's how to do it from your single workspace:

```powershell
cd C:\athena-workspace

# STEP 1: First, sync your public fork with the original (prevents errors!)
git fetch upstream
git checkout public
git merge upstream/main
git push public main

# STEP 2: Create a feature branch for your contribution
git checkout -b my-feature

# STEP 3: Make your changes and commit
git add .
git commit -m "Add my feature"

# STEP 4: Push to your PUBLIC fork (NOT origin - keep private work separate!)
git push public my-feature

# STEP 5: Create PR on GitHub
# Go to the ORIGINAL project: https://github.com/winstonkoh87/Athena-Public
# GitHub usually detects your branch and shows "Compare & pull request"
# Otherwise, click "New pull request" and select:
#   base: winstonkoh87:main  ← where you want changes to go
#   compare: YOUR-USERNAME:my-feature  ← your feature branch
```

### If You Haven't Created a Public Fork Yet

If you haven't created your public fork on GitHub yet:

1. Go to: https://github.com/winstonkoh87/Athena-Public
2. Click the **"Fork"** button (top right)
3. Select your GitHub account
4. Now you have `https://github.com/YOUR-USERNAME/Athena-Public`

Then add it as a remote in your workspace:

```powershell
cd C:\athena-workspace
git remote add public https://github.com/YOUR-USERNAME/Athena-Public.git
```

### Scenario 3: Updating Your Project with Latest Athena

After updating your workspace, update your project:

```powershell
cd C:\YOUR-PROJECT

# Run uv sync to get latest from local athena-sdk
uv sync

# Verify installation
python -m athena --help
```

### Key Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│               winstonkoh87/Athena-Public (original)                 │
│                                ↑                                    │
│                    [git remote: upstream]                           │
│                    ← fetch/merge                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    C:\athena-workspace (local workspace)             │
│                                                                     │
│   THREE REMOTES:                                                    │
│   • origin  → YOUR-private-repo (GitHub private)                    │
│   • public  → YOUR-fork (GitHub public)                             │
│   • upstream → winstonkoh87/Athena-Public (original)                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
| YOUR-private-   | | Athena-Public   | | C:\YOUR-PROJECT  |
| repo            | | (GitHub public)  | | (your project)   |
|                  | |                  | |                  |
| - Your work     | | - PR branches   | | - Uses athena    |
| - Backups        | | - Contributions | | - Syncs via uv   |
└──────────────────┘ └──────────────────┘ └──────────────────┘
           │                  │                  │
           │ (push)           │ (PR branches)    │ (uv sync)
           ▼                  ▼                  ▼
   Your private work   | Submit PRs here   |  Your actual project

```

---

## Troubleshooting: How to Know When to Sync

### Option 1: Watch the Repo on GitHub
1. Go to: https://github.com/winstonkoh87/Athena-Public
2. Click **"Watch"** (top right, bell icon)
3. Select **"All Activity"**
4. You'll get notifications for releases, PRs, issues

### Option 2: Check Before Starting Work
```powershell
cd C:\athena-workspace
git fetch upstream
git log upstream/main --oneline -5
```
This shows the 5 newest commits without changing anything.

### Option 3: Check for New Releases
```powershell
git fetch upstream
git tag --list | tail -5
```
Or watch https://github.com/winstonkoh87/Athena-Public/releases

---

## Troubleshooting: Non-Fast-Forward Error

### The Error
```
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/YOUR-USERNAME/Athena-Public.git'
hint: Updates were rejected because the tip of your current branch is behind
```

### What Happened
This usually means:
1. A PR was merged (someone's contribution was accepted!)
2. The upstream repo has new commits
3. Your local and remote are now out of sync

### The Fix
```powershell
# Step 1: Get latest from upstream
git fetch upstream
git merge upstream/main

# Step 2: Push to your public fork
git push public main

# Step 3: Create new PR if needed
```

---

## Troubleshooting: Unrelated Histories

### The Error
```
fatal: refusing to merge unrelated histories
```

### Why It Happens
This happens when your local repo and upstream have DIFFERENT histories - which occurs if you used the "Fork and Break" method (deleted .git and re-initialized).

### The Fix (One-Time Only)
```powershell
git merge upstream/main --allow-unrelated-histories -m "Merge upstream v9.2.7"
```

### Preview Changes BEFORE Merging
Want to see what will change without actually merging? Run:

```powershell
# See stats (files changed, lines added/deleted)
git diff --stat upstream/main

# See actual changes
git diff upstream/main
```

This is SAFE - it shows you what WOULD change without changing anything!

---

## After Your PR is Merged

### What Happens
When a PR is accepted:
1. Commits are added to the upstream repo
2. Local is now BEHIND (doesn't have the merge commit)
3. Public fork is also behind

### The Workflow
```powershell
# 1. Celebrate! 🎉 Your PR was merged!

# 2. Fetch latest from upstream
git fetch upstream

# 3. Merge into your local
git merge upstream/main

# 4. Push to both of your forks
git push origin main
git push public main

# 5. Your forks are now in sync with upstream
```

---

## Timeline of Errors and Solutions

| Step | Command | Error | Solution |
|------|---------|-------|----------|
| 1 | `pip install athena-ai` | PATH warning | Use `python -m pip` |
| 2 | `athena init --here --ide kilocode` | `--here` not found | N/A (wrong package) |
| 3 | `athena --help` | Only 2 options | N/A (wrong package) |
| 4 | `uv add athena-sdk` | Installed v0.0.1 | N/A (still wrong package) |
| 5 | Clone repo + `uv sync` | `athena` not recognized | Missing entry point |
| 6 | `python -m athena init --here --ide kilocode` | **SUCCESS** | Run as module |

---

## Final Working Configuration

```
C:\athena-workspace\          # Cloned GitHub repo (v9.2.6)
C:\your-project\                   # My project with Athena initialized
  .agent\                      # Athena workflows
  .framework\                  # Athena identity/laws
  .context\                    # Session logs/memory
  .kilocode\rules\athena.md   # Kilo Code integration
  .athena_root                 # Workspace marker
```

---

## TL;DR: Quick Reference

Run these commands from `C:\athena-workspace`:

| Task | Command |
|------|---------|
| Get original updates | `git fetch upstream && git merge upstream/main` |
| Push to both forks | `git push origin main && git push public main` |
| Update your project | `cd C:\YOUR-PROJECT && uv sync` |
| Contribute a fix | Create branch → `git push public my-branch` → PR on GitHub |
| Preview changes | `git diff --stat upstream/main` |
| Fix unrelated histories | `git merge upstream/main --allow-unrelated-histories` |

---

## Recommendations for the Maintainer

### 1. Fix the pip Package

The `athena-ai` package on PyPI (v0.0.12) is outdated and missing the CLI. Consider:
- Publishing `athena-sdk` v9.2.6 to PyPI
- Or updating `athena-ai` to match the GitHub repo

### 2. Add Console Script Entry Point

Add to `pyproject.toml`:
```toml
[project.scripts]
athena = "athena.__main__:main"
```

### 3. Update README with PowerShell Instructions when forking repo into private repo

Add a Windows/PowerShell section:
```markdown
## Windows PowerShell Users

# Delete .git folder (use PowerShell syntax):
Remove-Item -Recurse -Force .git

# If pip gives PATH warnings, use:
python -m pip install athena-ai
```

### 4. Clarify pip vs. Clone

The README should clearly state:
- `pip install athena-ai` = Basic SDK (limited features)
- Clone the repo = Full Athena system with CLI

---

## NEW ISSUE: UV Windows Editable Install Bug (Discovered via Kilo Code AI Agent)

### The Context

This bug was discovered while setting up the Athena package using **Kilo Code** (an AI coding agent that runs in VS Code). The AI agent was executing PowerShell commands through the VS Code terminal to install and configure Athena for the user's project.

This context is important because:
- The AI agent (Kilo Code) was running commands automatically
- All commands were executed through PowerShell in VS Code's terminal
- **The setup involved TWO separate workspaces:**
  - `C:\athena-workspace` = The Athena SDK source code
  - `C:\YOUR-PROJECT` = The user's project that uses Athena
- The issue might be specific to how AI agents handle command execution vs. manual user input
- The dual-workspace setup may have contributed to the issue (editable install linking across different paths)

### The Problem

On Windows 11 with UV (package manager), the command `uv pip install -e` does NOT create a proper editable install. Instead of creating a link to the source files, it copies the files to the virtual environment folder.

This means that any changes you make to files in your `C:\athena-workspace` folder will NOT be reflected in the virtual environment - you'll still be using the old copied files!

### Evidence

1. Check the `direct_url.json` file in the venv's dist-info folder:
   ```powershell
   Get-Content 'C:\YOUR-PROJECT\.venv\Lib\site-packages\athena_sdk-9.2.6.dist-info\direct_url.json'
   ```
   
   Expected: `{"dir_info":{"editable":true}}`
   Actual:   `{"dir_info":{"editable":false}}`

2. Compare file timestamps:
   ```powershell
   # Source file (your modified version)
   Get-ChildItem 'c:\athena-workspace\src\athena\__main__.py' | Select-Object LastWriteTime
   
   # Venv file (what Python actually uses)
   Get-ChildItem 'C:\YOUR-PROJECT\.venv\Lib\site-packages\athena\__main__.py' | Select-Object LastWriteTime
   ```
   
   If the source file is newer but Python still runs the old code, this confirms the bug.

### Root Cause

**This is a bug in UV on Windows.** When you run `uv pip install -e` (the `-e` flag means "editable"), UV is supposed to create a special link that tells Python to use the source files directly. However, on Windows:

1. **Windows requires Admin rights** to create proper symbolic links
2. **UV has a bug** where it doesn't use the Windows-compatible alternative method (called ".pth" files)
3. **Result:** UV falls back to copying files like a regular (non-editable) install

### The Workaround

After making any changes to your `C:\athena-workspace` files, you must manually copy the updated files to your project's venv:

```powershell
# Example: Copy the updated __main__.py to your project's venv
Copy-Item 'c:\athena-workspace\src\athena\__main__.py' 'C:\YOUR-PROJECT\.venv\Lib\site-packages\athena\__main__.py' -Force
```

Or completely reinstall:

```powershell
cd C:\YOUR-PROJECT
uv pip uninstall athena-sdk
uv pip install -e c:\athena-workspace
```

### Reporting the Bug

**If you encounter this bug, please report it to the UV team!** This helps everyone in the community.

To report:
1. Go to: https://github.com/astral-sh/uv/issues
2. Create a new issue
3. Include:
   - Your Windows version
   - The UV version (`uv --version`)
   - Steps to reproduce
   - The evidence (direct_url.json showing editable:false)
   - Mention that this was discovered while using an AI coding agent (Kilo Code) running PowerShell commands

---

## Conclusion

Athena is a powerful system, but the installation experience could be smoother for Windows users with existing private projects. The key issues are:

1. **Package confusion:** Multiple packages with different versions and features
2. **Missing entry point:** The GitHub repo doesn't create a working `athena` command
3. **PowerShell syntax:** Windows users need different commands than Linux/Mac
4. **Sync challenges:** Understanding how to keep local in sync with upstream

Despite these hurdles, the system works well once properly installed. This document should help future users avoid the same pitfalls.

---

*This document was created as a contribution to the Athena-Public project to help improve the onboarding experience for Windows/PowerShell users.*
