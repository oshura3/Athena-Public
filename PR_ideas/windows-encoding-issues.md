# Windows Encoding Issues in Athena Scripts

## Issue
When running Python scripts that use Unicode characters (emojis) on Windows, you may encounter:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f50d' in position 0: character maps to <undefined>
```

## Affected Scripts
- `.agent/scripts/core/smart_search.py` - uses emoji characters (🔍, 🧠, 🔤)

## Workaround
Set the `PYTHONIOENCODING` environment variable before running:

```cmd
set PYTHONIOENCODING=utf-8 && uv run .agent/scripts/core/smart_search.py "query"
```

## Permanent Fix Options

### Option 1: Add encoding declaration + use ASCII fallback
Add `# -*- coding: utf-8 -*-` at the top of the file and replace emojis with ASCII equivalents.

### Option 2: Set environment variable permanently
Add to your shell profile or create a batch file that sets the encoding before running scripts.

### Option 3: Use PYTHONIOENCODING globally
Add to system environment variables:
- Go to System Properties → Environment Variables
- Add new User variable: `PYTHONIOENCODING=utf-8`

## Notes
- This is a Windows-specific issue (cmd.exe uses CP1252 by default)
- PowerShell handles UTF-8 better but may need `chcp 65001`
- The scripts work correctly on Linux/macOS without modifications
