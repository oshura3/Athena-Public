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
from athena.utils.safe_print import get_divider_char

# Note: Unicode detection is now handled by the shared safe_print module
# No local _SUPPORTS_UNICODE needed - import from athena.utils.safe_print if needed


class UILoader:
    """UI utilities for formatting boot sequence output."""
    
    @staticmethod
    def divider(title: str):
        """Print a section divider.
        
        Uses Unicode box-drawing character (─) on Unicode-capable terminals,
        falls back to ASCII dashes (-) on Windows PowerShell with cp1252/cp437 encoding.
        
        Note: Now uses get_divider_char() from shared safe_print module.
        """
        # Use shared divider character from safe_print module
        div_char = get_divider_char()
        
        print(f"\n{BOLD}{CYAN}{div_char * 60}{RESET}")
        print(f"{BOLD}{CYAN}{title}{RESET}")
        print(f"{BOLD}{CYAN}{div_char * 60}{RESET}\n")

    @staticmethod
    def header(title: str, color: str = CYAN):
        """Print a header with optional color."""
        print(f"\n{BOLD}{color}{title}{RESET}")
