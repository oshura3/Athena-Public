"""Safe print utility for Windows console compatibility.

Provides safe_print() function that automatically converts emojis to ASCII
alternatives on Windows consoles that cannot encode Unicode characters.


## Why This Exists
-----------------

**Problem**: Windows cmd.exe and PowerShell consoles use legacy encodings
(cp1252 Western European or cp437 DOS) that cannot encode Unicode emoji 
characters. When Python's print() tries to output emoji, it raises:

    UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4dd'

**Solution**: This module provides safe_print() which:
1. Detects if the terminal encoding cannot handle Unicode
2. Automatically replaces emojis with ASCII fallbacks like [OK], [ERROR], etc.
3. Falls back gracefully - on Unix/Mac it prints emojis normally

**Usage**:
    from athena.utils.safe_print import safe_print
    safe_print("✅ Operation complete!")  # Prints [OK] on Windows, ✅ on Mac/Linux

**Fallback Mapping**:
    🩺 -> [CHECK]   ✅ -> [OK]   ⚠️ -> [WARNING]   ❌ -> [ERROR]
    🔑 -> [KEY]   📚 -> [DOCS]   📦 -> [PKG]   🚀 -> [LAUNCH]
    ...and many more

This is a project-wide solution to ensure Athena CLI works on all platforms.
"""
import sys
import os


def supports_unicode() -> bool:
    """Check if the terminal supports Unicode output.
    
    Returns False on Windows consoles with limited encoding (cp1252, cp437, etc.)
    to prevent UnicodeEncodeError when printing emojis and special characters.
    """
    if sys.platform == "win32":
        # Check Windows console encoding
        try:
            # Try to get the console output encoding
            if sys.stdout.encoding:
                encoding = sys.stdout.encoding.lower()
                # cp1252 (Windows Western European) doesn't support many emojis
                # cp437 (DOS) doesn't support Unicode
                if "cp1252" in encoding or encoding == "cp437":
                    return False
        except Exception:
            pass
        # Also check environment variable that PowerShell sets
        if os.environ.get("PYTHONIOENCODING"):
            encoding = os.environ.get("PYTHONIOENCODING", "").lower()
            if "cp1252" in encoding or encoding == "cp437":
                return False
    return True


# Unicode support detection - computed once at module load
_SUPPORTS_UNICODE = supports_unicode()

# Re-export for backwards compatibility (some files import from __main__)
# Import this module as: from athena.utils import safe_print
# Then access: safe_print.supports_unicode(), safe_print._SUPPORTS_UNICODE


def get_emoji_fallback():
    """Return emoji-to-ASCII fallback mapping for Windows consoles.
    
    This maps common emojis used in the CLI to ASCII alternatives.
    """
    return {
        "🩺": "[CHECK]",
        "✅": "[OK]",
        "⚠️": "[WARNING]",
        "❌": "[ERROR]",
        "🔑": "[KEY]",
        "📚": "[DOCS]",
        "📦": "[PKG]",
        "🚀": "[LAUNCH]",
        "🛑": "[STOP]",
        "💾": "[SAVE]",
        "⚙️": "[SETUP]",
        "🔍": "[SEARCH]",
        "🧠": "[ATHENA]",
        "🌐": "[NET]",
        "💻": "[DEV]",
        "📊": "[STATS]",
        "⏱️": "[TIME]",
        "✨": "[NEW]",
        "🔄": "[REFRESH]",
        "📝": "[NOTE]",
        "🎯": "[TARGET]",
        "🏗️": "[BUILD]",
        "🧪": "[TEST]",
        "⏭️": "[SKIP]",
        "📁": "[DIR]",
        "🧙‍♂️": "[WIZARD]",
        "👁️": "[VIEW]",
        "🏛️": "[ATHENA]",
        "🕸️": "[GRAPH]",
        "➡️": "->",
        "⬅️": "<-",
        "➖": "-",
        "➕": "+",
        "©": "(c)",
        "®": "(r)",
        "™": "(tm)",
    }


def get_box_drawing_fallback():
    """Return box-drawing character to ASCII fallback mapping.
    
    These Unicode box-drawing characters are used for UI dividers.
    """
    return {
        "─": "-",   # Horizontal line (U+2500)
        "━": "=",   # Heavy horizontal (U+2501)
        "│": "|",   # Vertical line (U+2502)
        "┃": "|",   # Heavy vertical (U+2503)
        "┌": "/",   # Top-left corner
        "┐": "\\",  # Top-right corner
        "└": "\\",  # Bottom-left corner
        "┘": "/",   # Bottom-right corner
        "├": "|",   # Left T
        "┤": "|",   # Right T
        "┬": "-",   # Top T
        "┴": "-",   # Bottom T
        "┼": "+",   # Cross
    }


def get_divider_char():
    """Get the appropriate divider character for the current terminal.
    
    Returns Unicode box-drawing character (─) on Unicode-capable terminals,
    returns ASCII dash (-) on Windows consoles with limited encoding.
    
    Usage:
        div = get_divider_char()
        print(f"{div * 40}")
    """
    if _SUPPORTS_UNICODE:
        return "─"  # Unicode box drawing horizontal
    else:
        return "-"  # ASCII fallback for Windows PowerShell


def safe_print(text: str):
    """Print text with Unicode fallback on non-Unicode consoles.
    
    If Unicode is not supported, replaces:
    - Emojis with ASCII alternatives (e.g., ✅ -> [OK])
    - Box-drawing characters with ASCII alternatives (e.g., ─ -> -)
    """
    if not _SUPPORTS_UNICODE:
        # Replace emojis
        emoji_map = get_emoji_fallback()
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        # Replace box-drawing characters
        box_map = get_box_drawing_fallback()
        for char, replacement in box_map.items():
            text = text.replace(char, replacement)
    print(text)
