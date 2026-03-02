import subprocess
import os
from athena.boot.constants import GREEN, RESET
from athena.utils.safe_print import safe_print


class SystemLoader:
    @staticmethod
    def verify_environment():
        """Titanium Airlock: Verifies dependencies and env vars."""
        from athena.boot.constants import PROJECT_ROOT, RED, YELLOW, BOLD, RESET, DIM

        ensure_env = (
            PROJECT_ROOT / "Athena-Public" / "examples" / "scripts" / "ensure_env.sh"
        )

        if not ensure_env.exists():
            safe_print(f"   ⚠️  Airlock: ensure_env.sh missing at {ensure_env}")
            return

        safe_print("🛡️  Verifying Environment (Airlock)...")
        result = subprocess.run(
            ["bash", str(ensure_env)], capture_output=True, text=True
        )
        if result.returncode != 0:
            safe_print(f"\n{RED}{BOLD}❌ Environment Check Failed{RESET}")
            safe_print(f"{DIM}{result.stdout}{RESET}")
            # Optional: Add auto-fix call here if desired
        else:
            safe_print(f"   {GREEN}✅ Environment Healthy{RESET}")

    @staticmethod
    def enforce_daemon():
        """Ensures the Athena Daemon (athenad) is active."""
        from athena.boot.constants import PROJECT_ROOT, GREEN, BOLD, RESET

        daemon_script = PROJECT_ROOT / "src" / "athena" / "core" / "athenad.py"

        try:
            # Check if running
            check = subprocess.run(["pgrep", "-f", "athenad.py"], capture_output=True)
            if check.returncode != 0:
                safe_print("🧠 Starting Athena Daemon (Titanium)...")
                subprocess.Popen(
                    [os.sys.executable, str(daemon_script)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                safe_print(f"   {GREEN}✅ Daemon Started.{RESET}")
            else:
                safe_print(f"   {GREEN}✅ Athena Daemon active.{RESET}")
        except Exception as e:
            safe_print(f"   ⚠️  Daemon enforcement failed: {e}")

    @staticmethod
    def sync_ui():
        """Launch UI components and sync hardware state."""
        safe_print(f"🔄 Syncing UI Components...")

        # Antigravity Launch with GPU flags
        cmd = [
            "open",
            "-a",
            "Antigravity",
            "--args",
            "--disable-gpu-driver-bug-workarounds",
            "--ignore-gpu-blacklist",
            "--enable-gpu-rasterization",
        ]

        try:
            # We use Popen to not block the boot sequence
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            safe_print(f"   {GREEN}✅ Antigravity Sync Initiated{RESET}")
        except Exception as e:
            safe_print(f"   ⚠️  Failed to sync Antigravity: {e}")
