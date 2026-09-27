#!/usr/bin/env python3
"""
install.py - One-Click Installer & Bootstrapper for Remember-Me (v2)
Cross-platform: Windows, macOS, Linux
Installs Remember-Me into Antigravity, Claude Code, Codex, and Cursor,
sets up behavioral reflex rules, and triggers inline index synchronization.
"""

import re
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

__version__ = "2.0.0"

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MARKER_START = "<!-- REMEMBER-ME-START -->"
MARKER_END = "<!-- REMEMBER-ME-END -->"
REFLEX_HEADER = "Remember-Me: Autonomous Skill Recall Reflex"


def load_rule_text() -> str:
    """Load base behavioral rule text from rules/remember-me.md."""
    rule_file = Path(__file__).resolve().parent / "rules" / "remember-me.md"
    if not rule_file.exists():
        print(f"  [-] Error: Required file not found: {rule_file}", file=sys.stderr)
        sys.exit(1)
    return rule_file.read_text(encoding="utf-8")


def install_skill_files(home: Path, repo_dir: Path) -> int:
    """Copy SKILL.md and scripts to standard skill locations."""
    skill_src = repo_dir / "SKILL.md"
    sync_src = repo_dir / "sync_skills_index.py"
    installed = 0

    targets = [
        ("Antigravity/Gemini", home / ".gemini" / "config" / "skills" / "remember-me", home / ".gemini"),
        ("Claude Code", home / ".claude" / "skills" / "remember-me", home / ".claude"),
        ("Codex / Open-Source Agents", home / ".agents" / "skills" / "remember-me", home / ".agents"),
    ]

    # Optional Codex directory if present
    if (home / ".codex").exists():
        targets.append(("Codex Direct", home / ".codex" / "skills" / "remember-me", home / ".codex"))

    for label, dest_dir, parent_check in targets:
        if parent_check.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
            scripts_dir = dest_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            if skill_src.exists():
                shutil.copy2(skill_src, dest_dir / "SKILL.md")
            if sync_src.exists():
                shutil.copy2(sync_src, scripts_dir / "sync_skills_index.py")
            print(f"  [+] Installed skill package ({label}) to: {dest_dir}")
            installed += 1

    return installed


def setup_gemini(home: Path, rule_text: str) -> bool:
    """Inject base behavioral rule into Antigravity/Gemini."""
    rules_dir = home / ".gemini" / "config" / "rules"
    if not rules_dir.parent.exists() and not (home / ".gemini").exists():
        return False
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / "remember-me.md"
    rule_file.write_text(rule_text, encoding="utf-8")
    print(f"  [+] Antigravity rule planted: {rule_file}")
    return True


def inject_marked_file(target_file: Path, inner_content: str, header: str = "## Remember-Me Skill Recall Reflex") -> bool:
    """Inject or update a marked block safely without regex backreference issues."""
    marked_block = f"{MARKER_START}\n{header}\n\n{inner_content.strip()}\n{MARKER_END}\n"

    if target_file.exists():
        content = target_file.read_text(encoding="utf-8", errors="ignore")
        start_idx = content.find(MARKER_START)
        end_idx = content.find(MARKER_END)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            updated = content[:start_idx] + marked_block + content[end_idx + len(MARKER_END):].lstrip("\r\n")
            target_file.write_text(updated.strip() + "\n", encoding="utf-8")
            print(f"  [~] Updated existing reflex in: {target_file}")
            return True
        elif header in content:
            idx = content.find(header)
            if idx != -1:
                base = content[:idx].rstrip()
                updated = (base + "\n\n" if base else "") + marked_block
                target_file.write_text(updated.strip() + "\n", encoding="utf-8")
                print(f"  [~] Upgraded legacy reflex in: {target_file}")
                return True
        updated = content.rstrip() + "\n\n" + marked_block
        target_file.write_text(updated.strip() + "\n", encoding="utf-8")
        print(f"  [+] Injected reflex into existing: {target_file}")
    else:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(marked_block.strip() + "\n", encoding="utf-8")
        print(f"  [+] Created: {target_file}")
    return True


def setup_claude(home: Path, rule_text: str) -> bool:
    """Inject behavioral rule into Claude Code CLAUDE.md."""
    claude_dir = home / ".claude"
    if not claude_dir.exists():
        return False
    claude_md = claude_dir / "CLAUDE.md"
    return inject_marked_file(claude_md, rule_text)


def setup_codex(home: Path, rule_text: str) -> bool:
    """Inject behavioral rule into Codex / Open-Source AGENTS.md."""
    configured = False
    for parent_dir, filename in [(home / ".agents", "AGENTS.md"), (home / ".codex", "AGENTS.md")]:
        if parent_dir.exists():
            target_file = parent_dir / filename
            if inject_marked_file(target_file, rule_text):
                configured = True
    return configured


def setup_cursor(home: Path, rule_text: str) -> bool:
    """Inject behavioral rule into Cursor IDE (.cursor/rules/)."""
    cursor_dir = home / ".cursor"
    if not cursor_dir.exists():
        return False
    rules_dir = cursor_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / "remember-me.mdc"
    content = (
        "---\n"
        "description: Remember-Me skill recall reflex with embedded compact catalog\n"
        "globs:\n"
        "alwaysApply: true\n"
        "---\n\n"
        + rule_text
    )
    rule_file.write_text(content, encoding="utf-8")
    print(f"  [+] Cursor rule planted: {rule_file}")
    return True


def run_sync(repo_dir: Path):
    """Run indexer to compile inline catalog directly into rule files."""
    sync_script = repo_dir / "sync_skills_index.py"
    if not sync_script.exists():
        return
    print("\n[*] Compiling and embedding inline skill catalog into rule files...")
    try:
        res = subprocess.run(
            [sys.executable, str(sync_script)],
            capture_output=True, text=True, check=True
        )
        print(res.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"  [-] Indexer failed (exit {e.returncode}): {e.stderr.strip()}", file=sys.stderr)
    except Exception as e:
        print(f"  [-] Error syncing index: {e}", file=sys.stderr)


def clean_marker_from_file(file_path: Path) -> bool:
    """Remove Remember-Me marker block from a file, deleting file if empty."""
    if not file_path.exists():
        return False
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    start_idx = content.find(MARKER_START)
    end_idx = content.find(MARKER_END)
    cleaned = None
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = (content[:start_idx] + content[end_idx + len(MARKER_END):]).strip()
    elif "Remember-Me Skill Recall Reflex" in content:
        idx = content.find("## Remember-Me Skill Recall Reflex")
        if idx != -1:
            cleaned = content[:idx].strip()

    if cleaned is not None:
        if cleaned:
            file_path.write_text(cleaned + "\n", encoding="utf-8")
            print(f"  [x] Removed reflex block from: {file_path}")
        else:
            file_path.unlink()
            print(f"  [x] Removed empty file: {file_path}")
        return True
    return False


def uninstall(home: Path):
    """Remove all Remember-Me artifacts from all agent platforms."""
    print("\n[*] Removing Remember-Me artifacts...")
    removed = 0

    targets = [
        home / ".gemini" / "config" / "skills" / "remember-me",
        home / ".gemini" / "config" / "rules" / "remember-me.md",
        home / ".gemini" / "config" / "SKILLS_INDEX.md",
        home / ".claude" / "skills" / "remember-me",
        home / ".claude" / "SKILLS_INDEX.md",
        home / ".agents" / "skills" / "remember-me",
        home / ".agents" / "SKILLS_INDEX.md",
        home / ".codex" / "skills" / "remember-me",
        home / ".codex" / "SKILLS_INDEX.md",
        home / ".cursor" / "rules" / "remember-me.mdc",
    ]

    for target in targets:
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            print(f"  [x] Removed: {target}")
            removed += 1

    # Clean CLAUDE.md and AGENTS.md injections
    if clean_marker_from_file(home / ".claude" / "CLAUDE.md"):
        removed += 1
    if clean_marker_from_file(home / ".agents" / "AGENTS.md"):
        removed += 1
    if clean_marker_from_file(home / ".codex" / "AGENTS.md"):
        removed += 1

    if removed == 0:
        print("  [=] Nothing to remove — Remember-Me was not installed.")
    else:
        print(f"\n  Cleaned {removed} artifact(s). Remember-Me has been fully uninstalled.")


def main():
    parser = argparse.ArgumentParser(
        description="Remember-Me v2: Skill Recall System Installer",
        epilog="Run with --uninstall to cleanly remove all Remember-Me artifacts."
    )
    parser.add_argument(
        "--uninstall", action="store_true",
        help="Remove all Remember-Me artifacts from all agent platforms"
    )
    args = parser.parse_args()

    user_home = Path.home()

    if args.uninstall:
        print("=" * 65)
        print("  Remember-Me: Uninstaller")
        print("=" * 65)
        uninstall(user_home)
        return

    print("=" * 65)
    print("  Remember-Me v2: Inline Skill Recall Bootstrapper")
    print("=" * 65)

    repo_dir = Path(__file__).resolve().parent
    rule_text = load_rule_text()

    print("\n[*] Deploying Skill Definition & Scripts...")
    installed = install_skill_files(user_home, repo_dir)

    print("\n[*] Installing Agent Behavioral Rules...")
    agents_found = 0
    if setup_gemini(user_home, rule_text):
        agents_found += 1
    if setup_claude(user_home, rule_text):
        agents_found += 1
    if setup_codex(user_home, rule_text):
        agents_found += 1
    if setup_cursor(user_home, rule_text):
        agents_found += 1

    if agents_found == 0 and installed == 0:
        print("\n  [!] WARNING: No agent configuration directories found.")
        print("      Expected at least one of:")
        print(f"        - {user_home / '.gemini'}  (Antigravity / Gemini)")
        print(f"        - {user_home / '.claude'}  (Claude Code)")
        print(f"        - {user_home / '.agents'}  (Codex / Open-Source Agents)")
        print(f"        - {user_home / '.codex'}   (Codex CLI)")
        print(f"        - {user_home / '.cursor'}  (Cursor IDE)")
        print("      Install one of these agents first, then re-run this installer.")
        sys.exit(1)

    run_sync(repo_dir)

    print("\n" + "=" * 65)
    print("  Installation Complete! Remember-Me v2 is active.")
    print("  Architecture : Inline Compact Index (Zero I/O, Instant Recall)")
    print("  Default mode : AUTO (announce & activate)")
    print("  Switch mode  : /remember-me whisper (ask before activating)")
    print("  Refresh index: /remember-me sync (or python sync_skills_index.py)")
    print("  Uninstall    : python install.py --uninstall")
    print("=" * 65)


if __name__ == "__main__":
    main()
