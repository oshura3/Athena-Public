# Athena Workspace Sync Guide

> **Purpose:** Step-by-step instructions for syncing the athena-private workspace with upstream and copying all necessary files to the PJ project workspace.
> 
> **Context:** This guide is based on the athena-private workspace setup documented in `../athena-private/docs/ATHENA_INSTALLATION_GUIDE.md`.

---

## Prerequisites

### Current Setup
```
C:\athena-private\          # Athena SDK (source of updates)
C:\PJ\                      # Your project (uses Athena)
```

### Three-Remote Configuration
Your athena-private workspace should have:
| Remote | GitHub Repo | Purpose |
|--------|-------------|---------|
| `origin` | PROJECT-athena (private) | Your personal work + backups |
| `public` | Athena-Public (public) | For submitting PRs to original |
| `upstream` | winstonkoh87/Athena-Public | Receiving updates from original |

---

## Step 1: Sync athena-private with Upstream

Open a **new terminal** and run:

```powershell
# Navigate to athena-private workspace
cd C:\athena-private

# Verify remotes are configured
git remote -v
```

**Expected output:**
```
origin    https://github.com/oshura3/PROJECT-athena.git (fetch)
origin    https://github.com/oshura3/PROJECT-athena.git (push)
public    https://github.com/oshura3/Athena-Public.git (fetch)
public    https://github.com/oshura3/Athena-Public.git (push)
upstream  https://github.com/winstonkoh87/Athena-Public.git (fetch)
upstream  https://github.com/winstonkoh87/Athena-Public.git (push)
```

### Fetch and View Upstream Changes

```powershell
# Fetch latest from upstream
git fetch upstream

# See what's new (last 16 commits)
git log HEAD..upstream/main --oneline
```

### Merge Upstream Changes

```powershell
# Merge into your private main branch
git merge upstream/main
```

**If you get "unrelated histories" error:**
```powershell
git merge upstream/main --allow-unrelated-histories
```

### Push to Both Forks

```powershell
# Push to your private fork (origin)
git push origin main

# Push to your public fork (public) - for PRs
git push public main
```

---

## Step 2: Update PJ Project with Latest Athena

```powershell
# Navigate to your project
cd C:\PJ

# Re-sync dependencies to get latest athena-sdk
uv sync

# Verify installation
python -m athena --help
```

---

## Step 3: Copy All Required Files to PJ

After syncing, you need to copy updated files from athena-private to PJ. Here's the complete list:

### Critical Files (Must Copy)

```powershell
# Core files - using Python for cross-platform compatibility
python -c "
import shutil
from pathlib import Path

src = Path(r'C:\athena-private')
dst = Path(r'C:\PJ')

# 1. Copy all protocols
shutil.copytree(src / 'examples/protocols', dst / '.agent/skills/protocols', dirs_exist_ok=True)

# 2. Copy all workflows
shutil.copytree(src / 'examples/workflows', dst / '.agent/workflows', dirs_exist_ok=True)

# 3. Copy core scripts
shutil.copytree(src / 'src/athena/scripts/core', dst / '.agent/scripts/core', dirs_exist_ok=True)

# 4. Copy lib folder (REQUIRED for script dependencies!)
shutil.copytree(src / 'examples/scripts/lib', dst / '.agent/scripts/lib', dirs_exist_ok=True)

# 5. Copy tutorial (if exists)
if (src / 'examples/workflows/tutorial.md').exists():
    shutil.copy2(src / 'examples/workflows/tutorial.md', dst / '.agent/workflows/tutorial.md')

print('✅ All files copied successfully!')
"
```

### Optional: Copy Additional Resources

```powershell
python -c "
import shutil
from pathlib import Path

src = Path(r'C:\athena-private')
dst = Path(r'C:\PJ')

# Copy examples scripts (if needed)
if (src / 'examples/scripts').exists():
    # Be careful here - these may have dependencies
    pass

# Copy docs (optional, for reference)
shutil.copytree(src / 'docs', dst / 'docs_atena_reference', dirs_exist_ok=True)

print('✅ Additional files copied!')
"
```

---

## Step 4: Sync User Profile (Important!)

To ensure Athena works the same regardless of which workspace you're in:

```powershell
# Copy user profile to athena-private
Copy-Item 'C:\PJ\.context\memories\user_profile.md' 'C:\athena-private\.context\memories\user_profile.md'

# Also ensure it's in PJ
# (should already be there from previous sessions)
```

---

## Step 5: Test the Setup

After copying all files, verify everything works:

### Test 1: Quicksave Script

```powershell
cd C:\PJ
set PYTHONIOENCODING=utf-8 && uv run .agent/scripts/quicksave.py "Sync test checkpoint"
```

**Expected output:**
```
✅ Quicksave → 2026-XX-XX-session-XX.md
```

### Test 2: Smart Search

```powershell
cd C:\PJ
set PYTHONIOENCODING=utf-8 && uv run .agent/scripts/core/smart_search.py "test" --limit 1
```

### Test 3: Run /tutorial (if available)

In Kilo Code, try:
```
/tutorial
```

---

## Version Tracking

| Component | Version | Last Updated |
|-----------|---------|--------------|
| Athena SDK | 9.2.6 → 9.2.7 (pending) | 2026-02-27 |
| PJ Project | Current | 2026-02-27 |
| Issues Found | 5 (see below) | 2026-02-27 |

### Issues Discovered (for bug reporting)

1. **Missing lib/ folder** - Scripts fail with `ModuleNotFoundError: No module named 'lib.shared_utils'`
   - Discovered: 2026-02-27
   - File version: quicksave.py from athena-private (pre-sync)
   - Workaround: Copy `examples/scripts/lib/` to `.agent/scripts/lib/`

2. **Hardcoded search paths** - smart_search.py pointed to wrong directories
   - Discovered: 2026-02-27
   - File version: smart_search.py from athena-private (pre-sync)
   - Fixed by updating SEARCHABLE_DIRS

3. **Windows encoding issues** - Emoji characters fail on cmd.exe
   - Discovered: 2026-02-27
   - Workaround: Set `PYTHONIOENCODING=utf-8`

4. **Missing tutorial workflow** - /tutorial command not available
   - Discovered: 2026-02-27
   - Workaround: Copy `examples/workflows/tutorial.md`

5. **Incomplete init** - Many files not copied during initialization
   - Discovered: 2026-02-27
   - Files affected: protocols/, workflows/, scripts/, lib/

---

## How Git Sync Actually Works

### What Happens During Fetch + Merge

1. **Fetch** - Downloads new commits from upstream (doesn't change your files yet)
2. **Merge** - Applies those commits to your local files:
   - **New files** → Added to your local workspace
   - **Modified files** → Updated to the new version
   - **Deleted files** → Removed from your local (if upstream deleted them)

### Understanding Your Three-Remote Setup

```
winstonkoh87/Athena-Public (upstream - original)
         ↓ (git fetch upstream)
  C:\athena-private (your local)
         ↓ (git push origin main)
  oshura3/pj-athena (private repo)
         ↓ (git push public main)
  oshura3/Athena-Public (public fork for PRs)
```

This flow ensures:
- ✅ All three repos stay in sync
- ✅ You can create PRs from your public fork
- ✅ Your private work is preserved in pj-athena

---

## Troubleshooting

### "unrelated histories" Error
```powershell
git merge upstream/main --allow-unrelated-histories
```

### Preview Changes Before Merging
```powershell
# See what files will change
git diff --stat upstream/main

# See actual changes
git diff upstream/main
```

### Non-Fast-Forward Error
```powershell
git fetch upstream
git merge upstream/main
git push public main
```

### CONFLICTS: How to Handle

#### What is a Conflict?
A conflict happens when:
- You edited a file locally
- Upstream ALSO changed that same file
- Git can't automatically decide which version to keep

#### How You'll Know
When you run `git merge upstream/main`, if there's a conflict you'll see:
```
Auto-merging src/athena/__main__.py
CONFLICT (content): Merge conflict in src/athena/__main__.py
Automatic merge failed; fix conflicts and then commit the result.
```

#### How to Resolve

**Step 1: See what files have conflicts**
```powershell
git status
```

**Step 2: Open the conflicted file**
You'll see markers like this:
```
<<<<<<< HEAD
# Your local changes
def main():
    print("My version")
=======
# Upstream changes
def main():
    print("Their version")
>>>>>>> upstream/main
```

**Step 3: Choose which version to keep**

Option A - Keep YOUR version:
```
def main():
    print("My version")
```

Option B - Keep THEIR version:
```
def main():
    print("Their version")
```

Option C - Combine both:
```
def main():
    print("My version")
    print("Their version")
```

**Step 4: Save the file and tell Git it's resolved**
```powershell
git add "path/to/file.py"
```

**Step 5: Complete the merge**
```powershell
git commit -m "Merge upstream - resolved conflicts"
```

#### Pro Tip: Abort Merge If Needed
If things get messy, you can cancel:
```powershell
git merge --abort
```
This reverts everything back to before you tried to merge.

---

## Complete Workflow Summary

```
1. cd C:\athena-private
2. git fetch upstream
3. git merge upstream/main
4. git push origin main
5. git push public main
6. cd C:\PJ
7. uv sync
8. [Run Python copy script from Step 3]
9. Copy user profile to athena-private
10. Test with quicksave
```

---

*Last updated: 2026-02-27*
*Guide based on: athena-private/docs/ATHENA_INSTALLATION_GUIDE.md*
