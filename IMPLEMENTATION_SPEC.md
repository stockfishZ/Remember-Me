# 🧠 Remember-Me v2: Inline Index Architecture

> **Purpose of this document:** A complete implementation specification so that any AI coding agent can implement the architectural change flawlessly without prior context.

---

## 1. Executive Summary

Remember-Me v1 tells the agent to read an external `SKILLS_INDEX.md` file every turn. This creates per-turn file I/O overhead and token bloat. **v2 eliminates the external file entirely** by embedding a compact skill index directly inside the rule files that are already loaded into the agent's system prompt.

**The single change:** `sync_skills_index.py` stops writing `SKILLS_INDEX.md` and instead regenerates the rule files (`rules/remember-me.md`, `CLAUDE.md` injection, `.cursor/rules/remember-me.mdc`) with the compact index embedded inline.

---

## 2. Why — The Statistical Case

### 2.1 Measured Data (1,017 installed skills)

These numbers were measured on a real system with 958 global skills + 59 plugin skills:

| Metric | Platform Default | Current Remember-Me v1 | **Proposed v2** |
|:---|---:|---:|---:|
| **Tokens in system prompt** | 58,042 | 200 | **5,793** |
| **File reads per turn** | 0 | 1 | **0** |
| **Tokens read per turn (file I/O)** | 0 | 20,287 | **0** |
| **Total per-turn token cost** | **58,042** | **20,487** | **5,793** |
| **Skills discoverable** | ~355 of 1,017 | all 1,017 | **all 1,017** |
| **Per-turn latency (file I/O)** | none | ~50-200ms | **none** |

### 2.2 Key Findings

1. **Platform default fails at scale.** With 1,017 skills, Antigravity/Claude inject ~58K tokens of skill descriptions into the system prompt. The context budget truncates **~65% of skills** (662 skills invisible).

2. **Current Remember-Me v1 is better but wasteful.** The rule (200 tokens) is tiny, but reading `SKILLS_INDEX.md` every turn costs **20,287 tokens** — that's 35% of the platform default cost, repeated on every single turn via file I/O.

3. **Proposed v2 is 90% cheaper than platform default, 72% cheaper than v1.** Embedding a compact name-only index in the rule file costs only **~5,793 tokens** in the system prompt, with zero file reads.

### 2.3 Per-Skill Token Economics

| Format | Chars/Skill | Tokens/Skill | 1,000 Skills Total |
|:---|---:|---:|---:|
| Platform default (name + path + full description) | ~228 | ~57 | ~57,000 |
| Current `SKILLS_INDEX.md` (name + truncated desc + path) | ~80 | ~20 | ~20,000 |
| **Proposed inline (name only, categorized)** | **~22** | **~5** | **~5,000** |

### 2.4 The "Why Not Just Descriptions?" Question

You might ask: "Why not include full descriptions in the inline index?" Because:

- At 1,000 skills, each extra word per skill adds ~1,000 tokens total
- Full descriptions cause prompt bloat and trigger false positives
- If the agent needs full guidelines, it reads the skill's `SKILL.md` on demand (which it already does today)

### 2.5 The "Cryptic Name" Flaw & The Smart Micro-Tag Solution

A pure name-only index suffers from a major blind spot: **Cryptic, abstract, or metaphorical skill names**.
- Skills like `grill-me`, `clarity-gate`, `vexor`, `loki-mode`, `kaizen`, `ponytail`, `fal-audio`, and `beautiful-prose` carry zero semantic clues to an LLM from their name alone. An agent would never associate "help me interview user requirements" with `grill-me`.
- **The Solution:** Hybrid Disambiguation via `is_cryptic()` and `clean_tag()`.
  - Obvious skills stay bare names: `postgresql`, `docker-expert`, `tailwind-patterns`.
  - Cryptic or ambiguous skills get a concise 2–4 word parenthetical intent tag: `grill-me (interview user requirements)`, `clarity-gate (rag verification)`, `vexor (vector code search)`.
  - **Token Impact:** Only ~32% of skills are tagged, adding merely ~1,500 tokens across 1,050+ skills, while achieving near 100% semantic recall accuracy.

---

## 3. What — The Architecture Change

### 3.1 Current Architecture (v1)

```
┌──────────────────────────┐     ┌────────────────────────┐
│ rules/remember-me.md     │     │ SKILLS_INDEX.md        │
│ (200 tokens, in prompt)  │────>│ (20K tokens, file I/O) │
│ "Go read the index file" │     │ Full table with descs  │
└──────────────────────────┘     └────────────────────────┘
         Always loaded               Read every turn
```

### 3.2 Proposed Architecture (v2)

```
┌─────────────────────────────────────────────┐
│ rules/remember-me.md                        │
│ (~5,800 tokens, in prompt)                  │
│                                             │
│ [Behavioral instructions]                   │
│ [Embedded compact index — names only]       │
│                                             │
│ ## Security & Pentesting                    │
│ owasp, xss-testing, idor-testing, iam...    │
│                                             │
│ ## Database & Data Storage                  │
│ postgresql, prisma, clickhouse, redis...    │
│                                             │
│ (... all categories ...)                    │
└─────────────────────────────────────────────┘
         Always loaded, zero file I/O
```

### 3.3 What Changes

| Component | v1 (Current) | v2 (Proposed) |
|:---|:---|:---|
| `rules/remember-me.md` | Static 29-line behavioral rule | Behavioral rule + embedded categorized index |
| `rules/CLAUDE.md` | Template with "read the file" instruction | Template with embedded index |
| `rules/AGENTS.md` | Template with "read the file" instruction | Template with embedded index |
| `SKILLS_INDEX.md` | Generated external file (primary artifact) | **Deleted / no longer generated** |
| `sync_skills_index.py` | Generates `SKILLS_INDEX.md` to config dirs | **Regenerates rule files with embedded index** |
| `install.py` | Copies rule files + runs sync | Copies rule files + runs sync (unchanged flow) |
| `SKILL.md` | References `SKILLS_INDEX.md` file | References inline index (no file reads) |

---

## 4. How — Implementation Details

### 4.1 Changes to `sync_skills_index.py`

This is the **primary file to modify.** The scanner and categorizer stay the same. Only the output format changes.

#### 4.1.1 Replace `generate_index_markdown()` with `generate_compact_index()`

The new function produces a **compact, name-only, categorized list** instead of a full markdown table:

```python
def generate_compact_index(skills: List[Dict[str, str]]) -> str:
    """Generate ultra-compact categorized skill index for rule embedding."""
    by_category: Dict[str, List[str]] = {}
    for s in skills:
        by_category.setdefault(s["category"], []).append(s["name"])

    lines = []
    for cat_name, _ in CATEGORY_RULES:
        cat_skills = by_category.get(cat_name, [])
        if not cat_skills:
            continue
        skill_list = ", ".join(sorted(cat_skills, key=str.lower))
        lines.append(f"### {cat_name} ({len(cat_skills)})")
        lines.append(skill_list)
        lines.append("")

    return "\n".join(lines)
```

**Example output:**

```markdown
### Security & Pentesting (23)
aws-security-audit, ffuf-claude-skill, find-bugs, idor-testing, owasp, pentest-checklist, pentest-commands, red-team-tactics, scanning-tools, vulnerability-scanner, xss-testing

### Database & Data Storage (12)
cc-skill-clickhouse-io, database-design, database-migrations, nosql-expert, postgresql, prisma-expert, sql-optimization-patterns, vector-index-tuning

### Cloud, DevOps & CI/CD (18)
aws-skills, docker-expert, helm-chart-scaffolding, k8s-manifest-generator, terraform-skill, vercel-deployment
```

#### 4.1.2 New function: `generate_rule_with_index()`

Composes the full rule file with embedded index:

```python
RULE_TEMPLATE = """# Remember-Me: Skill Recall

When your task involves a specialized domain and no obvious skill is already loaded,
scan the index below and read the matching skill's `SKILL.md` before proceeding.

- **`auto` mode (Default)**: Announce `⚡ [remember-me] Activated: <skill>`, load it, follow its rules.
- **`whisper` mode**: Ask user before loading: `💡 [remember-me] Found: <skill>. Use it?`
- **No match**: Proceed normally without delay.
- **Trivial tasks**: Skip this check for greetings, typo fixes, and simple questions.

Mode switches: `/remember-me auto` | `/remember-me whisper` | `/remember-me sync`

---

## Installed Skills Index ({total} skills)

{index}
"""


def generate_rule_with_index(skills: List[Dict[str, str]]) -> str:
    """Generate the complete rule file with embedded compact index."""
    index_body = generate_compact_index(skills)
    return RULE_TEMPLATE.format(total=len(skills), index=index_body)
```

#### 4.1.3 New function: `generate_claude_rule_with_index()`

Same concept but wrapped for `CLAUDE.md` injection:

```python
CLAUDE_TEMPLATE = """## Remember-Me Skill Recall Reflex

When your task involves a specialized domain and no obvious skill is already loaded,
scan the index below and read the matching skill's `SKILL.md` before proceeding.

- Default (`auto` mode): Announce `⚡ [remember-me] Activated: <skill>`, load and follow it.
- `whisper` mode: Ask confirmation before loading.
- No match: Proceed normally.

Mode: `/remember-me [auto|whisper|sync]`

### Installed Skills ({total} skills)

{index}
"""


def generate_claude_rule_with_index(skills: List[Dict[str, str]]) -> str:
    index_body = generate_compact_index(skills)
    return CLAUDE_TEMPLATE.format(total=len(skills), index=index_body)
```

#### 4.1.4 Update `main()` output targets

Replace the current `SKILLS_INDEX.md` file writes with **rule file regeneration**:

```python
def main():
    # ... (scanning logic stays identical) ...

    # Generate rule content with embedded index
    rule_content = generate_rule_with_index(all_skills)
    claude_content = generate_claude_rule_with_index(all_skills)

    # Write to Antigravity rule location
    gemini_rule = user_home / ".gemini" / "config" / "rules" / "remember-me.md"
    if gemini_rule.parent.exists():
        gemini_rule.write_text(rule_content, encoding="utf-8")
        print(f"Updated: {gemini_rule}")

    # Write to Claude CLAUDE.md (using existing marker-based injection)
    inject_into_claude_md(user_home, claude_content)

    # Write to Cursor rule location
    cursor_rule = user_home / ".cursor" / "rules" / "remember-me.mdc"
    if cursor_rule.parent.exists():
        cursor_content = (
            "---\n"
            "description: Remember-Me skill recall with embedded index\n"
            "globs:\n"
            "alwaysApply: true\n"
            "---\n\n"
            + rule_content
        )
        cursor_rule.write_text(cursor_content, encoding="utf-8")
        print(f"Updated: {cursor_rule}")

    # REMOVE old SKILLS_INDEX.md files if they exist (cleanup)
    for old_index in [
        user_home / ".gemini" / "config" / "SKILLS_INDEX.md",
        user_home / ".claude" / "SKILLS_INDEX.md",
    ]:
        if old_index.exists():
            old_index.unlink()
            print(f"Removed obsolete: {old_index}")
```

### 4.2 Changes to `install.py`

**Minimal changes required.** The `install.py` already:

1. Copies `SKILL.md` to skill directories (keep as-is)
2. Copies rule files to rule directories (keep as-is)
3. Calls `sync_skills_index.py` at the end (keep as-is — but sync now updates rule files)

The only change: **`load_rule_text()`** should be aware that the rule file might contain an embedded index (it gets regenerated by sync). The install flow should be:

1. `install.py` copies the **template** rule (without index) to the rule location
2. `install.py` calls `sync_skills_index.py`
3. `sync_skills_index.py` **overwrites** the rule files with the index-embedded versions

So `rules/remember-me.md` in the repo becomes a **template** that gets enriched by the sync script.

### 4.3 Changes to `SKILL.md`

Update the SKILL.md instructions to remove all references to reading `SKILLS_INDEX.md` as an external file. The skill description should reflect the new architecture:

**Before (line 31):**
```
- Location: Local configuration root (~/.gemini/config/SKILLS_INDEX.md, ~/.claude/SKILLS_INDEX.md, or ./SKILLS_INDEX.md).
```

**After:**
```
- The index is embedded directly in the agent's rule file. No external file read needed.
```

### 4.4 Changes to `rules/remember-me.md` (Template)

This file becomes the **base template** that `sync_skills_index.py` enriches. Keep it short:

```markdown
# Remember-Me: Skill Recall

When your task involves a specialized domain and no obvious skill is already loaded,
scan the index below and read the matching skill's SKILL.md before proceeding.

- **`auto` mode (Default)**: Announce activation, load it, follow its rules.
- **`whisper` mode**: Ask user before loading.
- **No match**: Proceed normally without delay.
- **Trivial tasks**: Skip this check for greetings, typo fixes, and simple questions.

Mode switches: `/remember-me auto` | `/remember-me whisper` | `/remember-me sync`

---

## Installed Skills Index

> Run `python sync_skills_index.py` to populate this section.
> The sync script will replace everything below this line with the categorized index.
```

### 4.5 Files to Delete

- Remove references to `SKILLS_INDEX.md` as an output target everywhere
- The sync script should actively delete old `SKILLS_INDEX.md` files during runs (cleanup)

---

## 5. Implementation Checklist
 
Use this checklist to verify completeness:
 
- [x] **`sync_skills_index.py`**: Replace `generate_index_markdown()` with `generate_compact_index()` (categorized, comma-separated with smart micro-tags for cryptic names)
- [x] **`sync_skills_index.py`**: Add `is_cryptic()` and `clean_tag()` for disambiguating metaphorical/abstract skill names
- [x] **`sync_skills_index.py`**: Add `generate_gemini_rule()` and `generate_claude_codex_block()` composing behavioral instructions + compact index
- [x] **`sync_skills_index.py`**: Add safe string-slicing marker injection for `CLAUDE.md`, `AGENTS.md`, and rule files
- [x] **`sync_skills_index.py`**: Update `main()` to write rule files across Antigravity, Claude Code, Codex, and Cursor
- [x] **`sync_skills_index.py`**: Add cleanup logic to delete obsolete `SKILLS_INDEX.md` files
- [x] **`rules/remember-me.md`**: Rewrite as a template with placeholder for the index section
- [x] **`rules/CLAUDE.md`**: Update template to reflect inline index (no file read instruction)
- [x] **`rules/AGENTS.md`**: Update template to reflect inline index for Codex / open-source agents
- [x] **`SKILL.md`**: Remove all references to `SKILLS_INDEX.md` file; document inline reflex & smart micro-tags
- [x] **`install.py`**: Support Codex (`AGENTS.md`), Claude Code (`CLAUDE.md`), Antigravity (`rules/remember-me.md`), and Cursor
- [x] **`README.md`**: Update architecture diagram, benchmarks, and multi-agent instructions
- [x] **Test**: Run `python sync_skills_index.py` and verify rule files contain the embedded index
- [x] **Test**: Run `python install.py --uninstall` and verify clean removal still works
- [x] **Test**: Run `python install.py` on a fresh setup and verify the full flow

---

## 6. Edge Cases and Gotchas

### 6.1 Rule File Size Limits

Some agent platforms may have per-rule-file size limits. At ~5,800 tokens (~23K chars) for 1,017 skills, this is well within reasonable limits. Monitor if platforms introduce caps.

### 6.2 Sync Must Be Idempotent

The sync script will be rewriting rule files. It must be safe to run multiple times. Use a clear delimiter/marker in the rule file so the sync script knows where the index section starts:

```markdown
<!-- REMEMBER-ME-INDEX-START -->
(generated content here)
<!-- REMEMBER-ME-INDEX-END -->
```

### 6.3 Install vs Sync Ordering

`install.py` copies the template rule, then `sync_skills_index.py` enriches it. If the user runs sync before install, the script should handle missing rule files gracefully (create them from scratch).

### 6.4 Backward Compatibility

Users upgrading from v1 will have `SKILLS_INDEX.md` files. The sync script should detect and remove these as part of its cleanup.

### 6.5 The Rule File is the Source of Truth

After sync runs, the rule file contains both the behavioral instructions AND the index. If a user manually edits the rule file, the next sync will overwrite their changes. Document this clearly.

---

## 7. Expected Outcome

After implementation, a user with 1,017 skills will see:

| Before (v1) | After (v2) |
|:---|:---|
| Rule says "go read a file" (200 tokens) | Rule contains everything (5,793 tokens) |
| File read every turn (20,287 tokens consumed per turn) | Zero file reads |
| Total per-turn cost: **20,487 tokens** | Total per-turn cost: **5,793 tokens** |
| Requires file I/O latency (~50-200ms) | Instant — already in memory |
| All 1,017 skills visible (via file) | All 1,017 skills visible (inline) |

**Net effect: 72% fewer tokens per turn, zero I/O latency, same coverage.**
