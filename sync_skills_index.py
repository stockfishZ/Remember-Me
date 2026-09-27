#!/usr/bin/env python3
"""
sync_skills_index.py - Automated Inline Skill Catalog Indexer for Agent Systems (v2)
Scans global and workspace skills directories, categorizes skills, extracts disambiguating
micro-tags for cryptic names, and embeds an ultra-compact index directly into agent rule files
(Antigravity, Claude Code, Codex, and Cursor).
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

__version__ = "2.0.0"

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MARKER_START = "<!-- REMEMBER-ME-START -->"
MARKER_END = "<!-- REMEMBER-ME-END -->"

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

COMMON_TECH_TERMS = {
    "python", "react", "vue", "angular", "node", "express", "fastapi", "django",
    "flask", "nextjs", "tailwind", "css", "html", "docker", "k8s", "kubernetes",
    "terraform", "aws", "azure", "gcp", "vercel", "postgres", "postgresql",
    "mysql", "sqlite", "redis", "mongodb", "prisma", "graphql", "rest", "api",
    "git", "github", "gitlab", "jira", "slack", "jest", "pytest", "playwright",
    "vitest", "tdd", "unit-testing", "security", "pentest", "vulnerability",
    "compliance", "linux", "bash", "powershell", "typescript", "javascript",
    "rust", "golang", "csharp", "dotnet", "laravel", "ruby", "rails"
}


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
    """Clean and condense description for processing."""
    if not desc:
        return "Specialized workflow and capabilities."
    cleaned = re.sub(r"^[>|\-]+\s*", "", desc)
    cleaned = cleaned.replace("—", "-").replace("–", "-")
    cleaned = re.sub(r"[`*_\[\]\n\r]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.strip("\"' ")
    if len(cleaned) > max_length:
        return cleaned[:max_length - 3].rstrip() + "..."
    return cleaned


def clean_tag(name: str, desc: str) -> str:
    """Extract a sharp 2-4 word intent tag for cryptic skill disambiguation."""
    if not desc:
        return ""
    d = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', desc)
    d = re.sub(r'[`*_#"\']', '', d).strip()

    prefixes = [
        r"^this skill should be used when the user asks to\s+",
        r"^this skill should be used when\s+",
        r"^use when you want to\s+",
        r"^use when you need to\s+",
        r"^use when the user asks to\s+",
        r"^use when the user mentions\s+",
        r"^use when working with\s+",
        r"^use when asking to\s+",
        r"^use when\s+",
        r"^when the user wants to\s+",
        r"^when the user asks to\s+",
        r"^when asked to\s+",
        r"^you are an?\s+",
        r"^you need to\s+",
        r"^stop and verify\s+",
        r"^guidelines for\s+",
        r"^how to\s+",
        r"^a guide (to|for)\s+",
        r"^expert (in|on|guide for)\s+",
        r"^senior \w+ engineer (for|role for)\s+",
        r"^opinionated, evolving constraints to guide agents when\s+",
        r"^a hybrid memory system that provides\s+",
        r"^automatically\s+",
        r"^master\s+",
        r"^comprehensive\s+"
    ]
    for p in prefixes:
        d = re.sub(p, '', d, flags=re.IGNORECASE).strip()

    first_clause = re.split(r'[\.\n;]|\s+-\s+', d)[0].strip()
    words = [w for w in first_clause.split() if w.lower() not in ('and', 'the', 'for', 'with', 'to', 'a', 'an') or w == first_clause.split()[0]]
    tag = " ".join(words[:4]).rstrip('.,:;()[]')
    if len(tag) > 32:
        tag = tag[:32].rsplit(' ', 1)[0]
    return tag.lower()


def is_cryptic(name: str, desc: str) -> bool:
    """Determine if a skill name is cryptic or ambiguous without a micro-tag."""
    name_lower = name.lower()
    tokens = set(re.split(r'[-_]', name_lower))

    # Well-known technical terms that are self-descriptive
    if any(t in COMMON_TECH_TERMS for t in tokens):
        if any(s in name_lower for s in ['automation', 'database', 'testing', 'expert', 'migration', 'patterns', 'guidelines']):
            return False

    # Common explicit automation or database connectors
    if name_lower.endswith('-automation') or name_lower.endswith('-database'):
        return False

    # Single-token names are almost always abstract/cryptic
    if len(tokens) == 1:
        return True

    # If the name does not share informative keywords with its description tag
    tag = clean_tag(name, desc)
    tag_tokens = set(re.split(r'[\s\-_]', tag)) - {'and', 'the', 'for', 'with', 'to', 'a', 'an'}
    overlap = tokens.intersection(tag_tokens)
    return len(overlap) == 0


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


def generate_compact_index(skills: List[Dict[str, str]]) -> Tuple[str, int]:
    """
    Generate ultra-compact, categorized, comma-separated skill list with
    smart micro-tags for cryptic names.
    Returns: (index_text, count_of_tagged_skills)
    """
    by_category: Dict[str, List[Dict[str, str]]] = {}
    for s in skills:
        by_category.setdefault(s["category"], []).append(s)

    lines = []
    tagged_count = 0

    for cat_name, _ in CATEGORY_RULES:
        cat_skills = by_category.get(cat_name, [])
        if not cat_skills:
            continue

        formatted_items = []
        for s in sorted(cat_skills, key=lambda x: x["name"].lower()):
            name = s["name"]
            desc = s["description"]
            if is_cryptic(name, desc):
                tag = clean_tag(name, desc)
                if tag and tag != name.lower():
                    formatted_items.append(f"{name} ({tag})")
                    tagged_count += 1
                else:
                    formatted_items.append(name)
            else:
                formatted_items.append(name)

        lines.append(f"### {cat_name} ({len(cat_skills)})")
        lines.append(", ".join(formatted_items))
        lines.append("")

    return "\n".join(lines).strip(), tagged_count


def generate_gemini_rule(skills: List[Dict[str, str]]) -> str:
    """Generate the full rule file for Antigravity / Gemini."""
    index_body, _ = generate_compact_index(skills)
    total = len(skills)
    return (
        "# Remember-Me: Autonomous Skill Recall Reflex\n\n"
        "When your task involves a specialized domain and no obvious skill is already loaded,\n"
        "scan the index below and read the matching skill's `SKILL.md` before proceeding.\n\n"
        "- **`auto` mode (Default)**: Announce `⚡ [remember-me] Activated skill: <skill-name>`, load its `SKILL.md`, and follow its workflows.\n"
        "- **`whisper` mode**: Ask confirmation before loading: `💡 [remember-me] I noticed this task relates to '<skill-name>'. Would you like me to follow its workflow?`\n"
        "- **No match**: Proceed normally without delay.\n"
        "- **Trivial tasks**: Skip this check for greetings, typo fixes, or basic one-liners.\n\n"
        "Mode switches: `/remember-me auto` | `/remember-me whisper` | `/remember-me sync`\n\n"
        "---\n\n"
        f"## Installed Skills Catalog ({total} skills)\n\n"
        f"{index_body}\n"
    )


def generate_claude_codex_block(skills: List[Dict[str, str]]) -> str:
    """Generate the marked block for CLAUDE.md and AGENTS.md."""
    index_body, _ = generate_compact_index(skills)
    total = len(skills)
    return (
        "## Remember-Me Skill Recall Reflex\n\n"
        "When your task involves a specialized domain and no obvious skill is already loaded,\n"
        "scan the index below and read the matching skill's `SKILL.md` before proceeding.\n\n"
        "- **`auto` mode (Default)**: Announce `⚡ [remember-me] Activated skill: <skill-name>`, load its `SKILL.md`, and follow its workflows.\n"
        "- **`whisper` mode**: Ask confirmation before loading: `💡 [remember-me] I noticed this task relates to '<skill-name>'. Would you like me to follow its workflow?`\n"
        "- **No match**: Proceed normally without delay.\n"
        "- **Trivial tasks**: Skip this check for greetings, typo fixes, or basic one-liners.\n\n"
        "Mode switches: `/remember-me auto` | `/remember-me whisper` | `/remember-me sync`\n\n"
        f"### Installed Skills Catalog ({total} skills)\n\n"
        f"{index_body}"
    )


def inject_marker_block(target_file: Path, block_content: str, header_hint: str = "Remember-Me") -> bool:
    """Inject or update a marked block in a markdown file cleanly and idempotently."""
    marked_block = f"{MARKER_START}\n{block_content.strip()}\n{MARKER_END}\n"

    if target_file.exists():
        content = target_file.read_text(encoding="utf-8", errors="ignore")
        start_idx = content.find(MARKER_START)
        end_idx = content.find(MARKER_END)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            updated = content[:start_idx] + marked_block + content[end_idx + len(MARKER_END):].lstrip("\r\n")
            target_file.write_text(updated.strip() + "\n", encoding="utf-8")
            return True
        elif header_hint in content:
            idx = content.find(f"## {header_hint}")
            if idx == -1:
                idx = content.find(f"# {header_hint}")
            if idx != -1:
                base = content[:idx].rstrip()
                updated = (base + "\n\n" if base else "") + marked_block
                target_file.write_text(updated.strip() + "\n", encoding="utf-8")
                return True
        updated = content.rstrip() + "\n\n" + marked_block
        target_file.write_text(updated.strip() + "\n", encoding="utf-8")
        return True
    else:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(marked_block.strip() + "\n", encoding="utf-8")
        return True


def cleanup_obsolete_index_files(user_home: Path, workspace: Optional[Path] = None):
    """Remove obsolete external SKILLS_INDEX.md files to prevent per-turn file reading."""
    candidates = [
        user_home / ".gemini" / "config" / "SKILLS_INDEX.md",
        user_home / ".claude" / "SKILLS_INDEX.md",
        user_home / ".agents" / "SKILLS_INDEX.md",
        user_home / ".codex" / "SKILLS_INDEX.md",
        Path(__file__).resolve().parent / "SKILLS_INDEX.md"
    ]
    if workspace:
        candidates.append(workspace / "SKILLS_INDEX.md")

    removed_count = 0
    for c in candidates:
        if c.exists():
            try:
                c.unlink()
                print(f"  [x] Removed obsolete external index: {c}")
                removed_count += 1
            except Exception as e:
                print(f"  [-] Failed to delete {c}: {e}", file=sys.stderr)
    return removed_count


def main():
    parser = argparse.ArgumentParser(
        description="Remember-Me v2: Inline Skill Catalog Indexer for Agent Systems"
    )
    parser.add_argument("--workspace", type=str, help="Workspace directory path to scan and inject into")
    parser.add_argument("--claude", action="store_true", help="Force update Claude Code CLAUDE.md")
    parser.add_argument("--codex", action="store_true", help="Force update Codex AGENTS.md")
    parser.add_argument("--output", type=str, help="Optional custom output path for rule content")
    args = parser.parse_args()

    user_home = Path.home()
    workspace_path = Path(args.workspace).resolve() if args.workspace else None

    # Skill directories to scan
    scan_dirs = [
        user_home / ".gemini" / "config" / "skills",
        user_home / ".claude" / "skills",
        user_home / ".agents" / "skills",
        user_home / ".codex" / "skills",
    ]

    # Plugins directories
    gemini_plugins_dir = user_home / ".gemini" / "config" / "plugins"
    if gemini_plugins_dir.exists():
        for plugin in gemini_plugins_dir.iterdir():
            if plugin.is_dir() and (plugin / "skills").exists():
                scan_dirs.append(plugin / "skills")

    # Workspace skills if requested
    if workspace_path:
        for ws_sub in [workspace_path / ".agents" / "skills", workspace_path / ".claude" / "skills"]:
            if ws_sub.exists():
                scan_dirs.append(ws_sub)

    all_skills = []
    seen_names = set()

    for d in scan_dirs:
        if d.exists():
            for s in scan_directory(d):
                if s["name"] not in seen_names:
                    seen_names.add(s["name"])
                    all_skills.append(s)

    print(f"[*] Discovered {len(all_skills)} unique skills across {len([d for d in scan_dirs if d.exists()])} locations.")

    if not all_skills:
        print("  [!] Warning: No skills found. Verify that skill directories exist and contain SKILL.md files.",
              file=sys.stderr)
        return

    # Generate rule contents
    gemini_rule_text = generate_gemini_rule(all_skills)
    claude_codex_text = generate_claude_codex_block(all_skills)
    compact_index, tagged_count = generate_compact_index(all_skills)

    print(f"[*] Compiled inline catalog: {len(all_skills)} skills ({tagged_count} disambiguated with micro-tags).")

    updated_targets = []

    # 1. Antigravity / Gemini rule
    gemini_rule_file = user_home / ".gemini" / "config" / "rules" / "remember-me.md"
    if gemini_rule_file.parent.exists() or (user_home / ".gemini").exists():
        gemini_rule_file.parent.mkdir(parents=True, exist_ok=True)
        gemini_rule_file.write_text(gemini_rule_text, encoding="utf-8")
        updated_targets.append(gemini_rule_file)

    # 2. Claude Code CLAUDE.md injection
    claude_dir = user_home / ".claude"
    if claude_dir.exists() or args.claude:
        claude_md = claude_dir / "CLAUDE.md"
        inject_marker_block(claude_md, claude_codex_text)
        updated_targets.append(claude_md)

    # 3. Codex / AGENTS.md injection
    # Support ~/.codex/AGENTS.md and ~/.agents/AGENTS.md
    codex_dir = user_home / ".codex"
    if codex_dir.exists() or args.codex:
        codex_agents_md = codex_dir / "AGENTS.md"
        inject_marker_block(codex_agents_md, claude_codex_text)
        updated_targets.append(codex_agents_md)

    agents_dir = user_home / ".agents"
    if agents_dir.exists():
        agents_md = agents_dir / "AGENTS.md"
        inject_marker_block(agents_md, claude_codex_text)
        updated_targets.append(agents_md)

    # 4. Cursor IDE rule
    cursor_rules_dir = user_home / ".cursor" / "rules"
    if cursor_rules_dir.parent.exists():
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        cursor_rule_file = cursor_rules_dir / "remember-me.mdc"
        cursor_content = (
            "---\n"
            "description: Remember-Me skill recall reflex with embedded compact index\n"
            "globs:\n"
            "alwaysApply: true\n"
            "---\n\n"
            + gemini_rule_text
        )
        cursor_rule_file.write_text(cursor_content, encoding="utf-8")
        updated_targets.append(cursor_rule_file)

    # 5. Workspace target injections if specified
    if workspace_path and workspace_path.exists():
        ws_agents_md = workspace_path / "AGENTS.md"
        inject_marker_block(ws_agents_md, claude_codex_text)
        updated_targets.append(ws_agents_md)

        ws_claude_md = workspace_path / "CLAUDE.md"
        inject_marker_block(ws_claude_md, claude_codex_text)
        updated_targets.append(ws_claude_md)

    # 6. Custom output path
    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(gemini_rule_text, encoding="utf-8")
        updated_targets.append(out_path)

    for target in updated_targets:
        print(f"  [+] Updated inline rule target: {target}")

    # Clean up obsolete external SKILLS_INDEX.md files
    cleanup_obsolete_index_files(user_home, workspace_path)
    print("[*] Remember-Me v2 sync completed successfully.")


if __name__ == "__main__":
    main()
