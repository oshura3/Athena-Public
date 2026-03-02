# Windows Unicode Encoding Fix — Implementation Plan

> **Objective**: Fix `UnicodeEncodeError` on Windows consoles (cp1252/cp437) across all Athena CLI tools and generators.
> **Root Cause**: Windows consoles cannot encode emoji characters used in print statements.
> **Solution Pattern**: Use `safe_print()` function with emoji-to-ASCII fallback (already implemented in `__main__.py` and `cli/init.py`).

---

## Summary of Changes

### Already Fixed (in PR)
- ✅ `src/athena/__main__.py` — CLI entry point
- ✅ `src/athena/boot/loaders/ui.py` — UI loader
- ✅ `src/athena/cli/init.py` — Workspace initializer

### Files Needing Fix (25+ files)

| Priority | File Path | Emoji Count | Category |
|:---------|:----------|:-----------:|:---------|
| **P1** | `src/athena/cli/save.py` | 2 | CLI |
| **P1** | `src/athena/cli/doctor.py` | 1 | CLI |
| **P1** | `src/athena/tools/search.py` | 5 | Tools |
| **P1** | `src/athena/tools/agentic_search.py` | 6 | Tools |
| **P2** | `src/athena/tools/reranker.py` | 3 | Tools |
| **P2** | `src/athena/tools/public_sync.py` | 2 | Tools |
| **P2** | `src/athena/tools/macro_graph.py` | 2 | Tools |
| **P2** | `src/athena/tools/heartbeat.py` | 3 | Tools |
| **P2** | `src/athena/tools/content_gen.py` | 2 | Tools |
| **P3** | `src/athena/generators/generate_compound_assets.py` | 10 | Generators |
| **P3** | `src/athena/generators/generate_skill_index.py` | 1 | Generators |
| **P3** | `src/athena/generators/generate_weekly_review.py` | 2 | Generators |
| **P3** | `src/athena/generators/generate_tag_index.py` | 3 | Generators |
| **P3** | `src/athena/generators/generate_sfw_graph.py` | 2 | Generators |
| **P3** | `src/athena/generators/generate_session_tldrs.py` | 3 | Generators |
| **P3** | `src/athena/generators/generate_protocol.py` | 1 | Generators |
| **P3** | `src/athena/generators/generate_graph_vis.py` | 4 | Generators |
| **P3** | `src/athena/generators/generate_case_study.py` | 1 | Generators |
| **P4** | `src/athena/core/flight_recorder.py` | 1 | Core |
| **P4** | `src/athena/core/health.py` | 1 | Core |
| **P4** | `src/athena/core/ruin_check.py` | 1 | Core |
| **P4** | `src/athena/core/diagnostic_relay.py` | 1 | Core |
| **P4** | `src/athena/auditors/audit_personality.py` | 8 | Auditors |
| **P4** | `src/athena/auditors/audit_session_coverage.py` | 2 | Auditors |
| **P4** | `src/athena/auditors/audit_staleness.py` | 2 | Auditors |
| **P4** | `src/athena/auditors/audit_velocity.py` | 4 | Auditors |
| **P4** | `src/athena/auditors/audit_observations.py` | 5 | Auditors |
| **P4** | `src/athena/auditors/audit_antipatterns.py` | 6 | Auditors |
| **P4** | `src/athena/auditors/audit_imports.py` | 3 | Auditors |
| **P4** | `src/athena/boot/shutdown.py` | 4 | Boot |
| **P4** | `src/athena/boot/orchestrator.py` | 4 | Boot |
| **P4** | `src/athena/boot/loaders/memory.py` | 8 | Boot |
| **P4** | `src/athena/boot/loaders/system.py` | 6 | Boot |
| **P4** | `src/athena/boot/loaders/identity.py` | 6 | Boot |

---

## Solution Architecture

### Option A: Shared Utility Module (Recommended)

**Create**: `src/athena/utils/safe_print.py`

```python
"""Safe print utility for Windows console compatibility."""
import sys
import os

def supports_unicode() -> bool:
    """Check if terminal supports Unicode."""
    if sys.platform == "win32":
        try:
            enc = sys.stdout.encoding.lower() if sys.stdout.encoding else ""
            if "cp1252" in enc or enc == "cp437":
                return False
        except Exception:
            pass
        py_enc = os.environ.get("PYTHONIOENCODING", "").lower()
        if "cp1252" in py_enc or py_enc == "cp437":
            return False
    return True

_SUPPORTS_UNICODE = supports_unicode()

# Complete emoji mapping
EMOJI_MAP = {
    "🩺": "[CHECK]", "✅": "[OK]", "⚠️": "[WARNING]", "❌": "[ERROR]",
    "🔑": "[KEY]", "📚": "[DOCS]", "📦": "[PKG]", "🚀": "[LAUNCH]",
    "🛑": "[STOP]", "💾": "[SAVE]", "⚙️": "[SETUP]", "🔍": "[SEARCH]",
    "🧠": "[ATHENA]", "🌐": "[NET]", "💻": "[DEV]", "📊": "[STATS]",
    "⏱️": "[TIME]", "✨": "[NEW]", "🔄": "[REFRESH]", "📝": "[NOTE]",
    "🎯": "[TARGET]", "🏗️": "[BUILD]", "🧪": "[TEST]", "⏭️": "[SKIP]",
    "📁": "[DIR]", "🧪": "[TEST]", "🔄": "[REFRESH]", "🕸️": "[GRAPH]",
    "🧙‍♂️": "[WIZARD]", "👁️": "[VIEW]", "🏛️": "[ATHENA]", "📦": "[DEPLOY]",
    "➡️": "->", "⬅️": "<-", "➖": "-", "➕": "+", "©": "(c)", "®": "(r)", "™": "(tm)",
}

def safe_print(text: str):
    """Print with emoji fallback for Windows."""
    if not _SUPPORTS_UNICODE:
        for emoji, replacement in EMOJI_MAP.items():
            text = text.replace(emoji, replacement)
    print(text)
```

**Update each file** to:
```python
# OLD
print("🧠 Message")

# NEW
from athena.utils.safe_print import safe_print
safe_print("🧠 Message")
```

### Option B: Copy-paste (Simpler but more duplication)

Same pattern as Options 1-2 but without the shared module. Each file gets its own copy of `safe_print()`.

**Pros**: No new module to import
**Cons**: Duplicated code across 25+ files

---

## Implementation Steps

### Phase 1: Create Utility Module
1. Create `src/athena/utils/` directory
2. Create `src/athena/utils/__init__.py`
3. Create `src/athena/utils/safe_print.py` with full emoji map

### Phase 2: Fix Priority 1 Files (CLI + Primary Tools)
| File | Changes Needed |
|:-----|:---------------|
| `cli/save.py` | Import + 2 print updates |
| `cli/doctor.py` | Import + 1 print update |
| `tools/search.py` | Import + 5 print updates |
| `tools/agentic_search.py` | Import + 6 print updates |

### Phase 3: Fix Priority 2 Files (Secondary Tools)
| File | Changes Needed |
|:-----|:---------------|
| `tools/reranker.py` | Import + 3 print updates |
| `tools/public_sync.py` | Import + 2 print updates |
| `tools/macro_graph.py` | Import + 2 print updates |
| `tools/heartbeat.py` | Import + 3 print updates |
| `tools/content_gen.py` | Import + 2 print updates |

### Phase 4: Fix Priority 3 Files (Generators)
| File | Changes Needed |
|:-----|:---------------|
| `generators/generate_*.py` (8 files) | Import + ~22 print updates total |

### Phase 5: Fix Priority 4 Files (Core, Auditors, Boot)
| File | Changes Needed |
|:-----|:---------------|
| `core/*.py` (4 files) | Import + 4 print updates |
| `auditors/audit_*.py` (6 files) | Import + ~30 print updates |
| `boot/shutdown.py` + others | Import + ~28 print updates |

---

## Testing Strategy

### Manual Test
```bash
# On Windows cmd.exe (cp437) or PowerShell (cp1252):
python -m athena init
python -m athena check
python -m athena save "test"
```

### Automated Test
Create `tests/test_windows_encoding.py`:
```python
def test_safe_print():
    """Verify safe_print doesn't raise UnicodeEncodeError."""
    import sys
    from io import StringIO
    
    # Capture output
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        safe_print("🧠 ATHENA")
        output = sys.stdout.getvalue()
        assert "[ATHENA]" in output
    finally:
        sys.stdout = old_stdout
```

---

## Documentation for Maintainer

### What Changed
- Added `safe_print()` utility function to handle Windows console encoding limitations
- Updated 25+ files to use `safe_print()` instead of `print()` with emojis

### Why It Changed
- Windows consoles (cmd.exe, PowerShell) use limited encodings (cp1252, cp437) that cannot encode most emoji characters
- This caused `UnicodeEncodeError` when running any Athena CLI command on Windows

### How to Maintain
- When adding new print statements with emojis, use `safe_print()` instead of `print()`
- Or use the ASCII alternatives directly: `[OK]`, `[ERROR]`, `[WARNING]`, etc.

### Emoji Reference
| Emoji | ASCII | Emoji | ASCII |
|:------|:------|:------|:------|
| ✅ | [OK] | ❌ | [ERROR] |
| ⚠️ | [WARNING] | 🧠 | [ATHENA] |
| 📁 | [DIR] | 📝 | [NOTE] |
| ⚙️ | [SETUP] | 🚀 | [LAUNCH] |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|:-----|:-----------:|:------:|:-----------|
| Breaking existing functionality | Low | High | All changes are additive (new function, no removal) |
| Missing emoji in fallback map | Medium | Low | Add missing emojis as they're discovered |
| Performance impact | Very Low | Low | Single string replacement, runs once per print |

---

## Commit Strategy

Following CONTRIBUTING.md guidelines: **One PR = one topic**, small atomic commits.

### Recommended Commit Messages (with body)

```bash
# Commit 1: Create shared utility module
git commit -m "feat: add safe_print utility for Windows console compatibility

Adds src/athena/utils/safe_print.py with:
- supports_unicode() to detect Windows console encoding (cp1252, cp437)
- safe_print() function with emoji-to-ASCII fallback mapping
- Complete emoji map covering all 50+ emojis used in the codebase

This allows all Athena CLI tools to work on Windows cmd.exe and PowerShell
without UnicodeEncodeError. Future emoji additions only need to update
this one file."

# Commit 2: Fix CLI tools
git commit -m "fix: apply Windows encoding fix to CLI tools

Updates print() calls with emojis to use safe_print():
- cli/save.py (2 emoji print statements)
- cli/doctor.py (1 emoji print statement)

No functional changes - only output formatting adaptation."

# Commit 3: Fix search tools
git commit -m "fix: apply Windows encoding fix to search tools

Updates print() calls with emojis to use safe_print():
- tools/search.py (5 emoji print statements)
- tools/agentic_search.py (6 emoji print statements)
- tools/reranker.py (3 emoji print statements, 2 already commented)

No functional changes - only output formatting adaptation."

# Commit 4: Fix secondary tools
git commit -m "fix: apply Windows encoding fix to secondary tools

Updates print() calls with emojis to use safe_print():
- tools/public_sync.py (2 emoji print statements)
- tools/macro_graph.py (2 emoji print statements)
- tools/heartbeat.py (3 emoji print statements)
- tools/content_gen.py (2 emoji print statements)

No functional changes - only output formatting adaptation."

# Commit 5: Fix generators
git commit -m "fix: apply Windows encoding fix to generators

Updates print() calls with emojis to use safe_print():
- generators/generate_compound_assets.py (10 emoji prints)
- generators/generate_skill_index.py (1 emoji print)
- generators/generate_weekly_review.py (2 emoji prints)
- generators/generate_tag_index.py (3 emoji prints)
- generators/generate_sfw_graph.py (2 emoji prints)
- generators/generate_session_tldrs.py (3 emoji prints)
- generators/generate_protocol.py (1 emoji print)
- generators/generate_graph_vis.py (4 emoji prints)
- generators/generate_case_study.py (1 emoji print)

No functional changes - only output formatting adaptation."

# Commit 6: Fix core modules
git commit -m "fix: apply Windows encoding fix to core modules

Updates print() calls with emojis to use safe_print():
- core/flight_recorder.py (1 emoji print)
- core/health.py (1 emoji print)
- core/ruin_check.py (1 emoji print)
- core/diagnostic_relay.py (1 emoji print)

No functional changes - only output formatting adaptation."

# Commit 7: Fix auditors
git commit -m "fix: apply Windows encoding fix to auditors

Updates print() calls with emojis to use safe_print():
- auditors/audit_personality.py (8 emoji prints)
- auditors/audit_session_coverage.py (2 emoji prints)
- auditors/audit_staleness.py (2 emoji prints)
- auditors/audit_velocity.py (4 emoji prints)
- auditors/audit_observations.py (5 emoji prints)
- auditors/audit_antipatterns.py (6 emoji prints)
- auditors/audit_imports.py (3 emoji prints)

No functional changes - only output formatting adaptation."

# Commit 8: Fix boot modules
git commit -m "fix: apply Windows encoding fix to boot modules

Updates print() calls with emojis to use safe_print():
- boot/shutdown.py (4 emoji prints)
- boot/orchestrator.py (4 emoji prints)
- boot/loaders/memory.py (8 emoji prints)
- boot/loaders/system.py (6 emoji prints)
- boot/loaders/identity.py (6 emoji prints)

No functional changes - only output formatting adaptation."

# Commit 9: Add test
git commit -m "test: add Windows encoding compatibility test

Adds tests/test_windows_encoding.py with:
- test_safe_print_unicode_support()
- test_safe_print_fallback()
- test_emoji_mapping_completeness()

Verifies safe_print() handles both Unicode and ASCII terminals correctly."
```

### Alternative: Single Comprehensive Commit

If preferred (less granular but simpler):

```bash
git commit -m "fix: resolve Windows console UnicodeEncodeError across CLI tools

Adds safe_print() utility to handle emoji output on Windows consoles
(cp1252, cp437 encodings that cannot encode emoji characters).

Files changed:
- Added: src/athena/utils/safe_print.py (new shared utility)
- Updated: 25+ files across cli/, tools/, generators/, core/, auditors/, boot/

No functional changes - only output formatting adaptation for Windows compatibility.
See plans/windows-encoding-fix-plan.md for full file list."
```

---

## Timeline

- **Phase 1**: ~10 minutes
- **Phase 2**: ~15 minutes
- **Phase 3**: ~15 minutes  
- **Phase 4**: ~20 minutes
- **Phase 5**: ~25 minutes

**Total estimated time**: ~90 minutes (sequential) or ~30 minutes (parallel with orchestrator)

---

## Open Questions

1. **Option A or B?** — Should we create a shared utility module or copy-paste the function?
2. **Commit granularity?** — One big commit vs. multiple small commits?
3. **Test coverage?** — Should we add automated tests now or later?

---

> **Plan created**: 2026-03-02  
> **Author**: Architect Agent  
> **For**: Windows Unicode Encoding Fix Initiative
