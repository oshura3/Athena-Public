"""
UI Loader Module
================

Provides UI utilities for the Athena boot sequence, including
section dividers and headers with color support.

Windows PowerShell Compatibility:
    On Windows consoles with limited encoding (cp1252, cp437), this module
    automatically falls back to ASCII characters (dashes) instead of
    Unicode box-drawing characters to prevent display issues.
"""

from athena.boot.constants import BOLD, CYAN, RESET

# Check Unicode support at module load time
# Import from __main__ to detect terminal capabilities
_SUPPORTS_UNICODE = True
try:
    # Import the function from the CLI entry point
    from athena.__main__ import supports_unicode
    _SUPPORTS_UNICODE = supports_unicode()
except Exception:
    pass  # Fallback to Unicode if detection fails


class UILoader:
    """UI utilities for formatting boot sequence output."""
    
    @staticmethod
    def divider(title: str):
        """Print a section divider.
        
        Uses Unicode box-drawing character (─) on Unicode-capable terminals,
        falls back to ASCII dashes (-) on Windows PowerShell with cp1252/cp437 encoding.
        """
        # Use ASCII dashes on Windows if Unicode is not supported
        if _SUPPORTS_UNICODE:
            div_char = "─"  # Unicode box drawing horizontal
        else:
            div_char = "-"  # ASCII fallback for Windows PowerShell
        
        print(f"\n{BOLD}{CYAN}{div_char * 60}{RESET}")
        print(f"{BOLD}{CYAN}{title}{RESET}")
        print(f"{BOLD}{CYAN}{div_char * 60}{RESET}\n")

    @staticmethod
    def header(title: str, color: str = CYAN):
        """Print a header with optional color."""
        print(f"\n{BOLD}{color}{title}{RESET}")
