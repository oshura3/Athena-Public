# Athena Installation Journey: Lessons Learned

> **Purpose:** Document the real-world experience of installing Athena in an existing private project by using a forked , including all errors, workarounds, and findings. This can help improve the onboarding experience for future users.

> **Author:** oshura3  
> **Date:** 2026-02-25  
> **Athena Version:** 9.2.6 (GitHub repo)  
> **Project:** [redacted] 
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
PS C:\athena-private> uv sync
Installed athena-sdk==9.2.6 (from file:///C:/athena-private)

# But even this version doesn't create a working 'athena' command!
PS C:\athena-private> athena --help
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
git clone https://github.com/winstonkoh87/Athena-Public.git athena-private
cd athena-private

# 2. BREAK the fork connection (PowerShell syntax!)
Remove-Item -Recurse -Force .git

# 3. Initialize a fresh private git history
git init
git add .
git commit -m "Initial Athena setup for PROJECTNAME project"

# 4. Create a new private repo on GitHub
#    Go to: https://github.com → + → New repository → Private

# 5. Connect your local copy to GitHub
git remote add origin https://github.com/YOUR-USERNAME/athena-private.git
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
cd C:\project
python -m athena init --here --ide kilocode
```

### What Finally Worked

```powershell
PS C:\project> python -m athena init --here --ide kilocode
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

- note: author added the scripts folder to PATH and still ended up using `python -m pip` to make everything work.

---

## Outstanding Concern: Updates

### The Problem

Since we're using a cloned repo and running via `python -m athena`, how do we keep Athena up to date?

### Possible Solutions

1. **Git pull in the cloned repo:**
   ```powershell
   cd C:\athena-private
   git pull origin main
   uv sync
   ```

2. **Add upstream remote (if forked):**
   ```powershell
   git remote add upstream https://github.com/winstonkoh87/Athena-Public.git
   git fetch upstream
   git merge upstream/main
   ```

3. **Wait for pip package update:** Hope that v9.2.6 or later gets published to PyPI with the full CLI.

### Recommended for Maintainer

Publish the full CLI version to PyPI so users can simply run:
```powershell
pip install athena-sdk  # Should install v9.2.6+ with full CLI
athena init --here --ide kilocode
```

---

## Protocol Recommendations for New Users

Based on the available protocols in `examples/protocols/`, here are recommendations for different use cases:

### For Project Management (Recommended for project)

| Protocol | ID | Category | Why Useful |
|----------|-----|----------|------------|
| **Context Engineering** | 240 | Engineering | Manage context window efficiently |
| **Efficiency-Robustness Tradeoff** | 49 | Decision | Navigate speed vs resilience decisions |
| **Premise Audit** | 111 | Decision | Validate assumptions before building |
| **Agent Swarm** | 416 | Workflow | Parallel multi-agent orchestration |

### For Code Quality

| Protocol | ID | Category | Why Useful |
|----------|-----|----------|------------|
| **BS Detection** | 47 | Pattern Detection | Identify unsound reasoning |
| **Cross-Model Validation** | 171 | Verification | Multi-model consensus checking |
| **Synthetic Deep Think** | 38 | Decision | Multi-layered reasoning |

### For Memory Management

| Protocol | ID | Category | Why Useful |
|----------|-----|----------|------------|
| **Semantic Compression** | - | Memory | Compress context efficiently |
| **Graph Memory Architecture** | - | Memory | Structure knowledge relationships |

### How to Copy Protocols

```powershell
# Copy specific protocols to your project
cp C:\athena-private\examples\protocols\decision\premise_audit.md C:\project\.agent\skills\protocols\
cp C:\athena-private\examples\protocols\engineering\context_engineering.md C:\project\.agent\skills\protocols\
```

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
C:\athena-private\          # Cloned GitHub repo (v9.2.6)
C:\project\                      # My project with Athena initialized
  .agent\                   # Athena workflows
  .framework\               # Athena identity/laws
  .context\                 # Session logs/memory
  .kilocode\rules\athena.md # Kilo Code integration
  .athena_root              # Workspace marker
```

---

## Next Steps for User

1. Follow remaining steps (5+) from discussion (https://github.com/winstonkoh87/Athena-Public/discussions/20#discussioncomment-15915354) 
2. Run `/start` in Kilo Code to boot Athena
3. Run `/tutorial` in Kilo Code to get acquainted with features
4. Copy relevant protocols from `C:\athena-private\examples\protocols\`
5. Configure environment variables (SUPABASE_URL, ANTHROPIC_API_KEY) for cloud features
6. Run `/end` when done working to save session

---

## Syncing with Upstream Athena-Public Project

### Understanding Your Three-Remote Setup

Your `C:\athena-private` workspace has THREE remotes configured. This is the key to managing both your private work AND contributing to the project:

| Remote | GitHub Repo | Purpose |
|--------|-------------|---------|
| `origin` | PROJECT-athena (private) | Your personal work + backups |
| `public` | Athena-Public (public) | For submitting PRs to original |
| `upstream` | winstonkoh87/Athena-Public | Receiving updates from original |

```powershell
# Your remote setup (verify with):
git remote -v
# Should show:
# origin    https://github.com/oshura3/PROJECT-athena.git (fetch)
# origin    https://github.com/oshura3/PROJECT-athena.git (push)
# public   https://github.com/oshura3/Athena-Public.git (fetch)
# public   https://github.com/oshura3/Athena-Public.git (push)
# upstream https://github.com/winstonkoh87/Athena-Public.git (fetch)
# upstream https://github.com/winstonkoh87/Athena-Public.git (push)
```

### Setting Up The Three Remotes

If you haven't set this up yet:

```powershell
cd C:\athena-private

# Already have origin? Skip to adding others
git remote -v

# Add your public fork (for PRs)
git remote add public https://github.com/YOUR-USERNAME/Athena-Public.git

# Add the original repo (for updates)
git remote add upstream https://github.com/winstonkoh87/Athena-Public.git
```

### Scenario 1: Keeping Your Private Athena Repo Updated (Development)

Your `C:\athena-private` repo contains your private modifications and should be kept in sync with the upstream Athena-Public repo to get the latest features and bug fixes.

```powershell
cd C:\athena-private

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
git push origin main      # Updates pj-athena (private)
git push public main      # Updates Athena-Public (public)

# Re-sync dependencies in your PROJECT project
cd C:\PROJECT
uv sync
```

### Scenario 2: Contributing to Athena-Public (Public PR Fork)

If you want to contribute to Athena-Public, you use your public fork. Here's how to do it from your single workspace:

```powershell
cd C:\athena-private

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
#   compare: oshura3:my-feature  ← your feature branch
```

### If You Haven't Created a Public Fork Yet

If you haven't created your public fork on GitHub yet:

1. Go to: https://github.com/winstonkoh87/Athena-Public
2. Click the **"Fork"** button (top right)
3. Select your GitHub account
4. Now you have `https://github.com/YOUR-USERNAME/Athena-Public`

Then add it as a remote in your workspace:

```powershell
cd C:\athena-private
git remote add public https://github.com/YOUR-USERNAME/Athena-Public.git
```

### Scenario 3: Updating Your PROJECT Project with Latest Athena

After updating your `C:\athena-private` repo, update your PROJECT project:

```powershell
cd C:\PROJECT

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
│                    C:\athena-private (local workspace)              │
│                                                                     │
│   THREE REMOTES:                                                    │
│   • origin  → PROJECT-athena (GitHub private)                       │
│   • public  → Athena-Public (GitHub public)                         │
│   • upstream → winstonkoh87/Athena-Public (original)                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
| PROJECT-athena   | | Athena-Public    | | C:\PROJECT       |
| (GitHub private) | | (GitHub public)  | | (your project)   |
|                  | |                  | |                  |
| - Your work      | | - PR branches    | | - Uses athena    |
| - Backups        | | - Contributions  | | - Syncs via uv   |
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │                  │                  │
          │ (push)           │ (PR branches)    │ (uv sync)
          ▼                  ▼                  ▼
  Your private work   | Submit PRs here   |  Your actual project

```

---

## Conclusion

Athena is a powerful system, but the installation experience could be smoother for Windows users with existing private projects. The key issues are:

1. **Package confusion:** Multiple packages with different versions and features
2. **Missing entry point:** The GitHub repo doesn't create a working `athena` command
3. **PowerShell syntax:** Windows users need different commands than Linux/Mac

Despite these hurdles, the system works well once properly installed. This document should help future users avoid the same pitfalls.

---

## TL;DR: Quick Reference

Run these commands from `C:\athena-private`:

| Task | Command |
|------|---------|
| Get original updates | `git fetch upstream && git merge upstream/main` |
| Push to both forks | `git push origin main && git push public main` |
| Update your project | `cd C:\PJ && uv sync` |
| Contribute a fix | Create branch → `git push public my-branch` → PR on GitHub |

---

*This document was created as a contribution to the Athena-Public project to help improve the onboarding experience.*