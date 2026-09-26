#!/usr/bin/env python3
"""
sync_skills_index.py - Automated Skill Catalog Indexer for Agent Systems
Scans global and workspace skills directories, parses metadata, and compiles
an ultra-compact, categorized SKILLS_INDEX.md for rapid agent recall.
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CATEGORY_RULES = [
    ("🛡️ Security & Pentesting", [
        r"\b(security|pentest|vulnerability|owasp|xss|idor|nmap|exploit|compliance|iam|hardening|crypto|cve|malware|red-team|reversing)\b"
    ]),
    ("🗄️ Database & Data Storage", [
        r"\b(database|postgres|postgresql|mysql|sqlite|nosql|mongodb|redis|clickhouse|bigquery|prisma|sql|migration|dbt|dynamodb|cassandra)\b"
    ]),
    ("🚀 Cloud, DevOps & CI/CD", [
        r"\b(cloud|devops|aws|azure|gcp|docker|k8s|kubernetes|terraform|helm|ci/cd|github-actions|gitlab|pipeline|vercel|render|deploy|serverless|nginx)\b"
    ]),
    ("🤖 AI, Agents & LLM", [
        r"\b(agent|agents|llm|langchain|langgraph|crewai|rag|prompt|openai|anthropic|gemini|embedding|vector|multi-agent|superpowers)\b"
    ]),
    ("🧪 Testing & QA", [
        r"\b(test|testing|tdd|unit-testing|jest|pytest|playwright|vitest|mock|profiling|benchmark|qa|code-review|coverage)\b"
    ]),
    ("⚙️ Backend & API", [
        r"\b(backend|node|express|fastapi|django|flask|dotnet|c#|laravel|rust|golang|go|java|spring|graphql|rest|trpc|api|microservice|ddd|grpc)\b"
    ]),
    ("🌐 Frontend, UI & Styling", [
        r"\b(react|vue|angular|tailwind|css|html|ui|ux|frontend|nextjs|svelte|astro|animation|remotion|canvas|figma|styling|components)\b"
    ]),
    ("💼 Integrations, CRM & Project Mgmt", [
        r"\b(jira|linear|clickup|trello|notion|asana|monday|todoist|slack|discord|github|gitlab|bitbucket|gmail|outlook|stripe|hubspot|salesforce|zendesk|intercom|miro)\b"
    ]),
    ("🔬 Science, Bio & Domain-Specific", [
        r"\b(bio|genom|protein|alphafold|blast|pdb|chembl|pubmed|uniprot|game|unity|unreal|godot|audio|transcriber|music)\b"
    ]),
    ("🛠️ Tools & General Dev", [])
]

def extract_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """Extract YAML frontmatter without external dependencies."""
    metadata = {}
    body = content
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        raw_yaml, body = match.groups()
        current_key = None
        current_val = []
        for line in raw_yaml.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            key_match = re.match(r"^([a-zA-Z0-9_\-]+)\s*:\s*(.*)$", line)
            if key_match:
                if current_key:
                    metadata[current_key] = " ".join(current_val).strip()
                current_key = key_match.group(1).lower()
                val_part = key_match.group(2).strip()
                if val_part in (">", "|", ">-", "|-"):
                    current_val = []
                else:
                    current_val = [val_part.strip("\"'")]
            elif current_key:
                current_val.append(line_str.strip("\"'"))
        if current_key:
            metadata[current_key] = " ".join(current_val).strip()
    return metadata, body

def clean_description(desc: str, max_length: int = 140) -> str:
    """Clean and condense description for rapid table scanning."""
    if not desc:
        return "Specialized workflow and capabilities."
    cleaned = re.sub(r"^[>|\-]+\s*", "", desc)
    cleaned = cleaned.replace("", "-").replace("—", "-").replace("–", "-")
    cleaned = re.sub(r"[`*_\[\]\n\r]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.strip("\"' ")
    if len(cleaned) > max_length:
        return cleaned[:max_length - 3].rstrip() + "..."
    return cleaned

def categorize_skill(name: str, desc: str) -> str:
    """Match skill name and description to an appropriate category."""
    name_lower = name.lower()
    desc_lower = desc.lower()
    for cat_name, patterns in CATEGORY_RULES:
        if not patterns:
            continue
        for pat in patterns:
            if re.search(pat, name_lower):
                return cat_name
    for cat_name, patterns in CATEGORY_RULES:
        if not patterns:
            continue
        for pat in patterns:
            if re.search(pat, desc_lower):
                return cat_name
    return "🛠️ Tools & General Dev"

def scan_directory(base_dir: Path) -> List[Dict[str, str]]:
    """Scan directory for subfolders containing SKILL.md."""
    skills = []
    if not base_dir.exists():
        return skills

    for item in sorted(base_dir.iterdir()):
        if item.is_dir():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                try:
                    content = skill_md.read_text(encoding="utf-8", errors="ignore")
                    meta, body = extract_frontmatter(content)
                    skill_name = meta.get("name", item.name)
                    desc = meta.get("description", "")
                    if not desc:
                        for line in body.splitlines():
                            line_s = line.strip()
                            if line_s and not line_s.startswith("#") and not line_s.startswith("-"):
                                desc = line_s
                                break
                    skills.append({
                        "name": skill_name,
                        "description": clean_description(desc),
                        "path": str(skill_md.resolve()).replace("\\", "/"),
                        "category": categorize_skill(skill_name, desc),
                        "source": str(base_dir.resolve()).replace("\\", "/")
                    })
                except Exception as e:
                    print(f"Warning reading {skill_md}: {e}", file=sys.stderr)
    return skills

def generate_index_markdown(skills: List[Dict[str, str]], target_path: Path) -> str:
    """Generate clean, categorized markdown index."""
    by_category: Dict[str, List[Dict[str, str]]] = {}
    for s in skills:
        by_category.setdefault(s["category"], []).append(s)

    lines = [
        "# SKILLS CATALOG INDEX (`SKILLS_INDEX.md`)",
        "",
        "> **Notice for AI Agents (Antigravity, Claude Code, Codex, Cursor):**",
        "> This index contains all installed skills and workflows. When user requests a non-trivial",
        "> task, check this catalog first. If a skill matches the user's intent:",
        "> - **In `auto` mode (Default)**: Announce `⚡ [remember-me] Activated skill: <name>`, read its `SKILL.md`, and apply it.",
        "> - **In `whisper` mode**: Ask user: `💡 [remember-me] I noticed this task matches <name>. Would you like to use it?`",
        "",
        f"**Total Skills Indexed:** {len(skills)} | **Auto-Generated & Synced**",
        "",
        "---",
        ""
    ]

    for cat_name, _ in CATEGORY_RULES:
        cat_skills = by_category.get(cat_name, [])
        if not cat_skills:
            continue
        lines.append(f"## {cat_name} ({len(cat_skills)})")
        lines.append("")
        lines.append("| Skill | Trigger Keywords & Summary | Path |")
        lines.append("| :--- | :--- | :--- |")
        for s in sorted(cat_skills, key=lambda x: x["name"].lower()):
            clean_name = f"`{s['name']}`"
            clean_desc = s["description"].replace("|", "/")
            lines.append(f"| {clean_name} | {clean_desc} | [{s['name']}](file:///{s['path']}) |")
        lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Sync skills index for agent recall")
    parser.add_argument("--gemini", action="store_true", default=True, help="Scan .gemini config skills")
    parser.add_argument("--claude", action="store_true", help="Also output to .claude directory")
    parser.add_argument("--workspace", type=str, help="Workspace path to include .agents/skills")
    parser.add_argument("--output", type=str, help="Custom output path for SKILLS_INDEX.md")
    args = parser.parse_args()

    user_home = Path.home()
    gemini_skills_dir = user_home / ".gemini" / "config" / "skills"
    claude_skills_dir = user_home / ".claude" / "skills"
    gemini_plugins_dir = user_home / ".gemini" / "config" / "plugins"

    all_skills = []
    seen_names = set()

    # 1. Global Gemini skills
    if gemini_skills_dir.exists():
        scanned = scan_directory(gemini_skills_dir)
        for s in scanned:
            if s["name"] not in seen_names:
                seen_names.add(s["name"])
                all_skills.append(s)

    # 2. Gemini plugin skills
    if gemini_plugins_dir.exists():
        for plugin in gemini_plugins_dir.iterdir():
            if plugin.is_dir() and (plugin / "skills").exists():
                scanned = scan_directory(plugin / "skills")
                for s in scanned:
                    if s["name"] not in seen_names:
                        seen_names.add(s["name"])
                        all_skills.append(s)

    # 3. Global Claude skills
    if claude_skills_dir.exists():
        scanned = scan_directory(claude_skills_dir)
        for s in scanned:
            if s["name"] not in seen_names:
                seen_names.add(s["name"])
                all_skills.append(s)

    # 4. Workspace skills
    if args.workspace:
        ws_path = Path(args.workspace)
        ws_skills = ws_path / ".agents" / "skills"
        if ws_skills.exists():
            scanned = scan_directory(ws_skills)
            for s in scanned:
                if s["name"] not in seen_names:
                    seen_names.add(s["name"])
                    all_skills.append(s)

    print(f"Discovered {len(all_skills)} unique skills across all sources.")

    outputs = []
    if args.output:
        outputs.append(Path(args.output))
    else:
        outputs.append(user_home / ".gemini" / "config" / "SKILLS_INDEX.md")
        if args.claude or (user_home / ".claude").exists():
            outputs.append(user_home / ".claude" / "SKILLS_INDEX.md")

    md_content = generate_index_markdown(all_skills, outputs[0])

    for out_path in outputs:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_content, encoding="utf-8")
        print(f"Successfully generated: {out_path}")

if __name__ == "__main__":
    main()
