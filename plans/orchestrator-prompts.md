# Orchestrator Prompt Design

> **Purpose**: Design prompts for the multi-agent Windows Encoding Fix workflow
> **Queen Bee**: Orchestrator that delegates to specialized drones
> **Drones**: Sub-agents that do specific tasks

---

## Overview

```
┌─────────────────────────────────────────────────────┐
│                  QUEEN BEE                          │
│         (Orchestrator Mode - Main)                 │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Drone 1 │ │  Drone 2 │ │  Drone N │            │
│  │  Utils   │ │  CLI Fix │ │  Tools   │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────┘
```

---

## Step 1: Queen Bee Prompt

The Queen Bee is the main orchestrator that manages the entire workflow.

> **Mode**: `orchestrator`

```markdown
# Windows Encoding Fix — Queen Bee Orchestrator

## Mission
Fix UnicodeEncodeError on Windows consoles (cp1252/cp437) across all Athena CLI tools.

## Context
- Root cause: Windows cmd.exe/PowerShell cannot encode emoji characters
- Solution: Use safe_print() with emoji-to-ASCII fallback
- Already fixed: src/athena/__main__.py, src/athena/cli/init.py (in PR)
- To fix: 25+ additional files (see file list)

## Workflow

### Phase 1: Create Utility Module
1. Create src/athena/utils/ directory
2. Create src/athena/utils/__init__.py  
3. Create src/athena/utils/safe_print.py with:
   - supports_unicode() function
   - EMOJI_MAP dictionary with all emojis
   - safe_print() function
4. **COMMIT AND PUSH after creating files** (CRITICAL)

### Phase 2: Fix Files by Category
For each category, spawn a drone with the appropriate prompt:

**CRITICAL: Each drone MUST commit and push after completing their files.**

**Drone Prompts (use these as templates):**

#### Drone: CLI Tools
- Target: cli/save.py, cli/doctor.py
- **Commit & Push AFTER fixing files**
- Prompt: [See Drone Template Below]

#### Drone: Search Tools  
- Target: tools/search.py, tools/agentic_search.py, tools/reranker.py
- **Commit & Push AFTER fixing files**
- Prompt: [See Drone Template Below]

#### Drone: Secondary Tools
- Target: tools/public_sync.py, tools/macro_graph.py, tools/heartbeat.py, tools/content_gen.py
- **Commit & Push AFTER fixing files**
- Prompt: [See Drone Template Below]

#### Drone: Generators
- Target: generators/generate_*.py (8 files)
- **Commit & Push AFTER fixing files**
- Prompt: [See Drone Template Below]

#### Drone: Core Modules
- Target: core/flight_recorder.py, core/health.py, core/ruin_check.py, core/diagnostic_relay.py
- **Commit & Push AFTER fixing files**
- Prompt: [See Drone Template Below]

#### Drone: Auditors
- Target: auditors/audit_*.py (7 files)
- **Commit & Push AFTER fixing files**
- Prompt: [See Drone Template Below]

#### Drone: Boot Modules
- Target: boot/shutdown.py, boot/orchestrator.py, boot/loaders/*.py (4 files)
- **Commit & Push AFTER fixing files**
- Prompt: [See Drone Template Below]

### Phase 3: Create Test
- Create tests/test_windows_encoding.py
- Include: test_safe_print_unicode_support, test_safe_print_fallback
- **COMMIT AND PUSH after creating test file**

## Constraints
- DO NOT modify functionality - only replace print() with safe_print()
- DO NOT add new features
- Keep all existing logic intact
- Test each change if possible

## File List (Copy for Reference)
See plans/windows-encoding-fix-plan.md for complete file list with emoji counts.
```

---

## Step 2: Drone File Updater Prompt

This is the template prompt that each drone uses to fix files.

> **Mode**: `code`

```markdown
# Drone: File Fixer — [CATEGORY NAME]

## Mission
Replace emoji print() statements with safe_print() for Windows compatibility.

## Context
- Root cause: Windows consoles (cp1252, cp437) cannot encode emojis
- Solution: Use safe_print() from athena.utils.safe_print
- Files already fixed: __main__.py, cli/init.py

## Files to Fix
[FILL IN FILE LIST WITH PATHS]

## Instructions

1. **Add import** (if not already present):
   ```python
   from athena.utils.safe_print import safe_print
   ```

2. **Replace print statements**:
   - Find all print() calls containing emojis
   - Replace with safe_print()
   
   Example:
   ```python
   # BEFORE
   print("🧠 ATHENA MESSAGE")
   print(f"   ✅ Success: {item}")
   
   # AFTER  
   safe_print("🧠 ATHENA MESSAGE")
   safe_print(f"   ✅ Success: {item}")
   ```

3. **Verify**:
   - Run: python -m athena [command] 
   - Ensure no UnicodeEncodeError on Windows

## AFTER COMPLETING FILE FIXES - COMMIT & PUSH

**This is critical - do this before the next drone starts:**

```bash
# Stage and commit
git add -A
git commit -m "[commit message - see below]"

# Push to BOTH remotes (CRITICAL for PR sync)
git push origin fix/windows-encoding-complete
git push public fix/windows-encoding-complete
```

## Commit Message for This Phase
```
fix: apply Windows encoding fix to [CATEGORY NAME]

Updates print() calls with emojis to use safe_print():
- [list files with emoji counts]

No functional changes - only output formatting adaptation.

Files: [list absolute paths]
```

## Emoji Reference
Use this mapping:
| Emoji | ASCII |
|:------|:------|
| ✅ | [OK] |
| ❌ | [ERROR] |
| ⚠️ | [WARNING] |
| 🧠 | [ATHENA] |
| 📁 | [DIR] |
| 📝 | [NOTE] |
| ⚙️ | [SETUP] |
| 🚀 | [LAUNCH] |
| (see full list in utils/safe_print.py) |

## DO
- Only change print() → safe_print()
- Keep all logic exactly the same
- Preserve formatting
- **COMMIT AND PUSH after completing files**

## DON'T
- Don't change functionality
- Don't add new features
- Don't remove code
- Don't change variable names
- Don't skip the commit/push step
```

---

## Step 3: Commit Message Creator Prompt

After all files are fixed, generate commit messages.

> **Mode**: `ask`

```markdown
# Drone: Commit Message Generator

## Context
You've fixed Windows Unicode encoding across the Athena CLI. Generate commit messages following CONTRIBUTING.md guidelines.

## Requirements
1. Use conventional commit format: type(scope): description
2. Include body with details
3. List specific files changed
4. Note "No functional changes"

## Categories Fixed
1. Utility module (new file)
2. CLI tools
3. Search tools  
4. Secondary tools
5. Generators
6. Core modules
7. Auditors
8. Boot modules
9. Tests

## Output Format
For each category, output:
```
git commit -m "[type]: [subject]

[Body explaining what was done and why]

Files: [list specific files]
Co-authored-by: Your Name <your@email>
"
```

## Example
```
fix: apply Windows encoding fix to CLI tools

Updates print() calls with emojis to use safe_print():
- cli/save.py (2 emoji print statements)
- cli/doctor.py (1 emoji print statement)

No functional changes - only output formatting adaptation.

Files: src/athena/cli/save.py, src/athena/cli/doctor.py
```
```

---

## Step 4: Git Push Prompt

Push all commits to the fork.

> **Mode**: `code`

```bash
# Add all changes
git add -A

# For each commit (in order):
git commit --amend -m "feat: add safe_print utility..."

# Push to your fork (public remote)
git push public main --force

# Create new branch for follow-up PR
git checkout -b fix/windows-encoding-complete
git push public fix/windows-encoding-complete
```

---

## Summary: 4-Step Workflow

| Step | Mode | Purpose |
|:-----|:-----|:--------|
| 1 | Architect | Design/plan (DONE) |
| 2 | Ask | Create Queen Bee + Drone prompts (IN PROGRESS) |
| 3 | Orchestrator | Execute using prompts above |
| 4 | Code | Push commits to fork |

---

## Ready to Proceed?

Once you approve these prompts, I'll:
1. Switch to Ask mode to finalize the prompts
2. Then switch to Orchestrator to execute

Or would you like me to make any edits to the prompts above first?