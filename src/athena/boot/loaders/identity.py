import sys
import json
import re
import hashlib
from pathlib import Path
from athena.boot.constants import (
    PROJECT_ROOT,
    CORE_IDENTITY,
    PROTOCOLS_JSON,
    EXPECTED_CORE_HASH,
    RED,
    GREEN,
    YELLOW,
    CYAN,
    BOLD,
    DIM,
    RESET,
)
from athena.utils.safe_print import safe_print


class IdentityLoader:
    @staticmethod
    def verify_semantic_prime() -> bool:
        """Verify Core_Identity.md integrity via SHA-384 hash."""
        if not CORE_IDENTITY.exists():
            safe_print(f"{RED}[FATAL] Core_Identity.md NOT FOUND{RESET}")
            safe_print(f"{RED}        Identity drift detected. Cannot boot.{RESET}")
            return False

        try:
            content = CORE_IDENTITY.read_bytes()
            current_hash = hashlib.sha384(content).hexdigest()
        except Exception as e:
            safe_print(f"{RED}[FATAL] Cannot read Core_Identity.md: {e}{RESET}")
            return False

        if EXPECTED_CORE_HASH is not None:
            if current_hash != EXPECTED_CORE_HASH:
                safe_print(f"{RED}{'=' * 60}{RESET}")
                safe_print(f"{RED}{BOLD}🚨 SEMANTIC PRIME INTEGRITY FAILURE 🚨{RESET}")
                safe_print(f"Expected: {EXPECTED_CORE_HASH[:32]}...")
                safe_print(f"Actual:   {current_hash[:32]}...")
                safe_print(f"{BOLD}REFUSING TO BOOT. Manual review required.{RESET}")
                return False
            else:
                safe_print(f"{GREEN}✅ Semantic prime verified (SHA-384 match){RESET}")
        else:
            safe_print(f"{DIM}Semantic prime: readable (no hash verification){RESET}")

        return True

    @staticmethod
    def display_cognitive_profile():
        """Reads and displays Section 0 and Section 5 of Athena Profile."""
        profile_path = (
            PROJECT_ROOT
            / ".framework"
            / "v8.2-stable"
            / "modules"
            / "Athena_Profile.md"
        )
        if not profile_path.exists():
            return

        try:
            content = profile_path.read_text(encoding="utf-8")
            safe_print(f"\n{BOLD}{CYAN}🧠 ATHENA COGNITIVE IDENTITY (Active){RESET}")

            # Extract Invariant Rules
            invariants_match = re.search(
                r"## 0\. Invariant Rules.*?\|(.*?)\|.*?\n\n", content, re.DOTALL
            )
            if invariants_match:
                safe_print(f"{BOLD}⚡ Invariant Rules:{RESET}")
                rows = [
                    line.strip()
                    for line in invariants_match.group(0).split("\n")
                    if "|" in line and "---" not in line and "Description" not in line
                ]
                for row in rows:
                    parts = [p.strip() for p in row.split("|") if p.strip()]
                    if len(parts) >= 2:
                        safe_print(f"   • {parts[0]}: {DIM}{parts[1]}{RESET}")

            safe_print(f"\n{BOLD}⚡ Cognitive Modes:{RESET}")
            safe_print(
                f"   • {GREEN}Bionic (Default){RESET}: Independent. Utility-Max. Stress-tests."
            )
            safe_print(f"   • {YELLOW}Proxy (Drafting){RESET}: Voice Only. No Thinking.")

        except Exception as e:
            safe_print(f"{YELLOW}⚠️ Failed to load Athena Profile: {e}{RESET}")

    @staticmethod
    def _get_protocol_cache_path():
        from athena.core.config import AGENT_DIR

        return AGENT_DIR / "state" / "protocol_cache.json"

    @staticmethod
    def inject_auto_protocols(context_clues=""):
        """Scans enabled protocols and injects relevant ones (with disk-backed caching)."""
        if not PROTOCOLS_JSON.exists():
            return

        cache_path = IdentityLoader._get_protocol_cache_path()
        context_key = context_clues.lower().strip()

        # Try cache first
        if cache_path.exists():
            try:
                cache = json.loads(cache_path.read_text())
                if context_key in cache:
                    # In a real system, we'd check if PROTOCOLS_JSON mtime changed
                    # But for now, simple cache return
                    cached_loadout = cache[context_key]
                    safe_print(
                        f"\n{BOLD}{CYAN}🧙‍♂️ ATHENA GUIDANCE SYSTEM (Cached Loadout){RESET}"
                    )
                    safe_print(f"{DIM}Detected Context: {context_clues}{RESET}")
                    safe_print(f"\n{BOLD}⚡ Active Context Loadout:{RESET}")
                    for p in cached_loadout:
                        safe_print(
                            f"   ► {p['icon']} {GREEN}{p['type']} {p['pid']}{RESET}: {p['name']}"
                        )
                        safe_print(f"     {DIM}Trigger: {p['trigger']}{RESET}")
                    return
            except Exception:
                pass

        try:
            with open(PROTOCOLS_JSON, "r") as f:
                data = json.load(f)
            protocols = data.get("protocols", {})
            active_context = context_clues.lower().split()

            matches = []
            for pid, p in protocols.items():
                protocol_path = p.get("path", "")
                if protocol_path:
                    full_path = PROJECT_ROOT / protocol_path
                    if not full_path.exists():
                        continue

                score = 0
                tags = [t.lower() for t in p.get("context_tags", [])]
                cases = [c.lower() for c in p.get("applied_use_cases", [])]

                for term in active_context:
                    if term in tags or any(term in t for t in tags):
                        score += 1
                for term in active_context:
                    if any(term in c for c in cases):
                        score += 2

                if score > 0:
                    matches.append((score, pid, p))

            matches.sort(key=lambda x: x[0], reverse=True)

            if matches:
                output_matches = []
                safe_print(f"\n{BOLD}{CYAN}🧙‍♂️ ATHENA GUIDANCE SYSTEM (Auto-Active){RESET}")
                safe_print(f"{DIM}Detected Context: {context_clues}{RESET}")
                safe_print(f"\n{BOLD}⚡ Active Context Loadout:{RESET}")
                for _, pid, p in matches[:5]:
                    name = p["name"]
                    ptype = p.get("type", "protocol").title()
                    cases = p.get("applied_use_cases", ["General Application"])
                    icon = "🧪" if ptype == "Case_Study" else "📜"
                    safe_print(f"   ► {icon} {GREEN}{ptype} {pid}{RESET}: {name}")
                    safe_print(f"     {DIM}Trigger: {cases[0]}{RESET}")

                    output_matches.append(
                        {
                            "pid": pid,
                            "name": name,
                            "type": ptype,
                            "trigger": cases[0],
                            "icon": icon,
                        }
                    )

                # Save to cache
                try:
                    cache = {}
                    if cache_path.exists():
                        cache = json.loads(cache_path.read_text())
                    cache[context_key] = output_matches
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_text(json.dumps(cache))
                except Exception:
                    pass
            else:
                safe_print(
                    f"\n{DIM}No specific context detected. Running Standard Operating Procedures.{RESET}"
                )

        except Exception as e:
            safe_print(f"{YELLOW}⚠️ Auto-Injection warning: {e}{RESET}")

    @staticmethod
    def display_cos_status():
        """Initializes and displays the state of the Committee of Seats."""
        try:
            from athena.core.cos import get_cos_engine

            if not get_cos_engine:
                safe_print(f"{YELLOW}⚠️ COS Engine not available{RESET}")
                return

            cos = get_cos_engine()
            seats = cos.active_seats
            safe_print(f"\n{BOLD}{CYAN}🏛️  COMMITTEE OF SEATS (COS) INITIALIZED{RESET}")
            safe_print(f"{DIM}Protocol 166 Proxy Engine Active{RESET}")
            seat_str = " | ".join([f"{GREEN}{s.value}{RESET}" for s in seats])
            safe_print(f"   Seats: {seat_str}")
        except ImportError:
            pass
