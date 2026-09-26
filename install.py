#!/usr/bin/env python3
"""
install.py - One-Click Installer & Bootstrapper for Remember-Me
Cross-platform: Windows, macOS, Linux
Installs the Remember-Me skill, plants behavioral rules into Antigravity,
Claude Code, and Cursor, and compiles the first SKILLS_INDEX.md catalog.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

RULE_TEXT = """# Remember-Me: Autonomous Skill Recall Reflex

## Core Directive
Before planning, scaffolding, or implementing any non-trivial user task (architecture, feature development, bug fixes, database design, testing, security, or integrations), you **MUST** perform a **Step 0: Skill Pre-flight Check**.

Do NOT assume you must implement everything from scratch. You have specialized skills installed across the system.

## Step 0 Execution
1. Check the local `SKILLS_INDEX.md` (in ~/.gemini/config/ or ~/.claude/ or workspace root) for skills whose domain, keywords, or triggers match the user's intent.
2. If a match is found:
   - **`auto` mode (Default)**:
     - Announce: `⚡ [remember-me] Activated skill: <skill-name>`
     - Read the skill's `SKILL.md` to adopt its exact rules and workflows.
     - Execute the task strictly adhering to that skill's guidelines.
   - **`whisper` mode**:
     - Pause and ask the user: `💡 [remember-me] I detected that your task relates to '<skill-name>'. Would you like me to follow its specialized workflow?`
     - Wait for user confirmation before loading the skill.
3. If no matching skill exists, proceed with standard expert reasoning without delay.

## Mode Controls
- The user may toggle modes at any time:
  - `/remember-me auto` or `/remember-me-auto` -> Autonomous activation (Default).
  - `/remember-me whisper` or `/remember-me-whisper` -> Prompt before activating.
  - `/remember-me sync` -> Refreshes the skills index.
- Mode persists across the session. When in doubt, default to `auto`.

## Exclusions
Skip the Step 0 check for trivial conversational replies, simple greetings, or brief single-sentence general knowledge questions.
"""

def install_skill_files(home: Path, repo_dir: Path):
    """Copy SKILL.md and scripts to standard skill locations."""
    skill_src = repo_dir / "SKILL.md"
    sync_src = repo_dir / "sync_skills_index.py"
    
    # 1. Antigravity/Gemini
    gemini_dest = home / ".gemini" / "config" / "skills" / "remember-me"
    if (home / ".gemini").exists():
        gemini_dest.mkdir(parents=True, exist_ok=True)
        (gemini_dest / "scripts").mkdir(parents=True, exist_ok=True)
        if skill_src.exists():
            shutil.copy2(skill_src, gemini_dest / "SKILL.md")
        if sync_src.exists():
            shutil.copy2(sync_src, gemini_dest / "scripts" / "sync_skills_index.py")
        print(f"  [+] Installed skill package to: {gemini_dest}")

    # 2. Claude Code
    claude_dest = home / ".claude" / "skills" / "remember-me"
    if (home / ".claude").exists():
        claude_dest.mkdir(parents=True, exist_ok=True)
        (claude_dest / "scripts").mkdir(parents=True, exist_ok=True)
        if skill_src.exists():
            shutil.copy2(skill_src, claude_dest / "SKILL.md")
        if sync_src.exists():
            shutil.copy2(sync_src, claude_dest / "scripts" / "sync_skills_index.py")
        print(f"  [+] Installed skill package to: {claude_dest}")

def setup_gemini(home: Path):
    """Inject behavioral rule into Antigravity/Gemini."""
    rules_dir = home / ".gemini" / "config" / "rules"
    if rules_dir.parent.exists():
        rules_dir.mkdir(parents=True, exist_ok=True)
        rule_file = rules_dir / "remember-me.md"
        rule_file.write_text(RULE_TEXT, encoding="utf-8")
        print(f"  [+] Antigravity rule planted: {rule_file}")

def setup_claude(home: Path):
    """Inject behavioral rule into Claude Code CLAUDE.md."""
    claude_dir = home / ".claude"
    if claude_dir.exists():
        claude_md = claude_dir / "CLAUDE.md"
        snippet = "\n\n## Remember-Me Skill Recall Reflex\n" + RULE_TEXT
        if claude_md.exists():
            existing = claude_md.read_text(encoding="utf-8", errors="ignore")
            if "Remember-Me: Autonomous Skill Recall Reflex" not in existing:
                claude_md.write_text(existing + snippet, encoding="utf-8")
                print(f"  [+] Injected reflex into existing: {claude_md}")
            else:
                print(f"  [=] Reflex already present in: {claude_md}")
        else:
            claude_md.write_text(snippet.strip(), encoding="utf-8")
            print(f"  [+] Created: {claude_md}")

def run_sync(repo_dir: Path):
    """Run indexer to compile initial SKILLS_INDEX.md."""
    sync_script = repo_dir / "sync_skills_index.py"
    if not sync_script.exists():
        return
    print("\n[*] Compiling and indexing all installed skills...")
    try:
        res = subprocess.run([sys.executable, str(sync_script)], capture_output=True, text=True, check=True)
        print(res.stdout.strip())
    except Exception as e:
        print(f"  [-] Error syncing index: {e}", file=sys.stderr)

def main():
    print("=" * 65)
    print("  Remember-Me: Skill Recall System Bootstrapper")
    print("=" * 65)

    user_home = Path.home()
    repo_dir = Path(__file__).resolve().parent

    print("\n[*] Deploying Skill Definition & Scripts...")
    install_skill_files(user_home, repo_dir)

    print("\n[*] Installing Agent Behavioral Rules...")
    setup_gemini(user_home)
    setup_claude(user_home)

    run_sync(repo_dir)

    print("\n" + "=" * 65)
    print("  Installation Complete! Remember-Me is active in your agent's brain.")
    print("  Default mode : AUTO (announce & activate)")
    print("  Switch mode  : /remember-me whisper (ask confirmation first)")
    print("  Refresh index: /remember-me sync (or python sync_skills_index.py)")
    print("=" * 65)

if __name__ == "__main__":
    main()
