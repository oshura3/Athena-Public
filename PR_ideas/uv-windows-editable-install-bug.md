# UV Windows Editable Install Bug Report

> **Purpose:** This is a dedicated bug report for the UV team regarding the editable install issue on Windows 11.
> **Date:** 2026-02-27
> **Reporter:** Community (discovered while setting up Athena with Kilo Code AI agent)

---

## Bug Summary

**Title:** `uv pip install -e` does not create proper editable install on Windows 11

**Severity:** High

**Environment:**
- OS: Windows 11 (version 23H2)
- **UV Version: 0.9.22** (found via `uv --version`)
- Python Version: 3.12
- Package Manager: UV

---

## Description

When running `uv pip install -e <path>` on Windows 11, the package is installed as a regular (non-editable) install instead of an editable install. This means changes to source files are not reflected when running the package.

---

## Steps to Reproduce

1. Create a Python project with source files (or use an existing one)
2. Open PowerShell in VS Code terminal (or regular PowerShell)
3. Run: `uv pip install -e <path-to-package>`
4. Modify a source file in the package
5. Run the package - changes are NOT reflected

---

## Expected Behavior

Editable installs should create a link to source files so changes are reflected immediately without reinstallation.

---

## Actual Behavior

Files are copied to the virtual environment, making it a regular (non-editable) install.

---

## Evidence

### Check 1: direct_url.json

Check the `direct_url.json` file in the dist-info folder:

```powershell
# Find the dist-info folder
Get-ChildItem 'C:\YOUR-PROJECT\.venv\Lib\site-packages' -Filter "*.dist-info"

# Check the direct_url.json content
Get-Content 'C:\YOUR-PROJECT\.venv\Lib\site-packages\athena_sdk-9.2.6.dist-info\direct_url.json'
```

**Expected:** `{"dir_info":{"editable":true}}`
**Actual (Verified):** `{"url":"file:///C:/athena-private","dir_info":{"editable":false}}`

### Check 2: File Timestamps

Compare file timestamps between source and venv:

```powershell
# Source file (your modified version)
Get-ChildItem 'c:\athena-workspace\src\athena\__main__.py' | Select-Object LastWriteTime

# Venv file (what Python actually uses)
Get-ChildItem 'C:\YOUR-PROJECT\.venv\Lib\site-packages\athena\__main__.py' | Select-Object LastWriteTime
```

If the source file is newer but Python still runs the old code, this confirms the bug.

---

## Additional Context

This bug was discovered while setting up the **Athena** project (an AI agent system) using **Kilo Code** (an AI coding agent that runs in VS Code). The AI agent was executing PowerShell commands through the VS Code terminal.

This context may be relevant because:
- The AI agent was running commands automatically (not manual user input)
- All commands were executed through PowerShell in VS Code's terminal
- **The setup involved TWO separate workspaces:**
  - `C:\athena-workspace` = The Athena SDK source code
  - `C:\YOUR-PROJECT` = The user's project that uses Athena
- The issue might be specific to how AI agents handle command execution
- The dual-workspace setup may have contributed to the issue (editable install linking across different paths)

---

## Workaround

After making any changes to source files, manually copy them to the venv:

```powershell
# Copy updated file to venv
Copy-Item 'c:\athena-workspace\src\athena\__main__.py' 'C:\YOUR-PROJECT\.venv\Lib\site-packages\athena\__main__.py' -Force
```

Or completely reinstall:

```powershell
cd C:\YOUR-PROJECT
uv pip uninstall athena-sdk
uv pip install -e c:\athena-workspace
```

---

## Suggested Fix

The UV team should investigate:
1. Proper handling of editable installs on Windows without admin privileges
2. Using .pth files as a Windows-compatible alternative to symlinks
3. Ensuring the `direct_url.json` correctly reflects `editable: true` when `-e` flag is used

---

## Related Issues

If you find this bug affects you, please add your experience to help the UV team track the scope of this issue.

---

*This bug report was created to help the UV team identify and fix the editable install issue on Windows.*
