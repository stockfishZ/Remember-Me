---
name: remember-me
description: "MANDATORY: Evaluated on ANY coding, design, debugging, database, architecture, or testing task. Checks the installed skills catalog (SKILLS_INDEX.md) to recall and activate matching specialized workflows. Modes: auto (default), whisper, sync. Also trigger on /remember-me, /remember-me-auto, /remember-me-whisper, 'remember skills', 'recall skills', or 'what skills do you have'."
argument-hint: "[auto|whisper|sync]"
license: MIT
---

# Remember-Me: Autonomous Skill Recall Reflex

Modern AI coding agents (Antigravity, Claude Code, Codex, Cursor) frequently suffer from the **Skill Discoverability Problem**: when users install dozens or hundreds of specialized skills, the agent's prompt context budget truncates or drops them. The agent literally forgets that specialized workflows exist.

**Remember-Me** is a cognitive reflex that solves this by maintaining a lightweight, categorized index (`SKILLS_INDEX.md`) and pre-flighting tasks against it before writing code.

---

## ⚡ Modes of Operation

| Mode | Trigger / Switch | Behavior |
| :--- | :--- | :--- |
| **`auto`** *(Default)* | `/remember-me auto`<br>`/remember-me-auto` | **Autonomous Activation**: The agent announces `⚡ [remember-me] Activated skill: <skill-name>`, loads `SKILL.md`, and follows its exact workflows immediately. |
| **`whisper`** | `/remember-me whisper`<br>`/remember-me-whisper` | **Confirmation-First**: The agent announces `💡 [remember-me] I noticed this task relates to '<skill-name>'. Would you like me to follow its specialized workflow?` and waits for user confirmation before proceeding. |
| **`sync`** | `/remember-me sync` | Runs the automated indexer script to refresh `SKILLS_INDEX.md` when new skills or plugins are installed. |

---

## 🧠 Step 0: The Pre-Flight Check

Before planning, creating code, modifying architectures, or proposing solutions for any non-trivial task:

1. **Scan `SKILLS_INDEX.md`**:
   - Location: Local configuration root (`~/.gemini/config/SKILLS_INDEX.md`, `~/.claude/SKILLS_INDEX.md`, or `./SKILLS_INDEX.md`).
   - Match the user's intent, domain, and keywords against the catalog.

2. **Categorized Domains Available**:
   - 🛡️ **Security & Pentesting**: OWASP, XSS, IDOR, IAM, hardening, red team
   - 🗄️ **Database & Data Storage**: PostgreSQL, Redis, ClickHouse, Prisma, schema migrations
   - 🚀 **Cloud, DevOps & CI/CD**: Docker, Kubernetes, Terraform, AWS, Azure, GCP, Vercel
   - 🤖 **AI, Agents & LLM**: Multi-agent systems, LangChain, RAG, prompt engineering, CrewAI
   - 🧪 **Testing & QA**: TDD, unit testing, Playwright, Jest, debugging, benchmarking
   - ⚙️ **Backend & API**: Express, FastAPI, Django, Go, Rust, .NET, GraphQL, DDD
   - 🌐 **Frontend, UI & Styling**: React, Tailwind, Next.js, animations, design systems
   - 💼 **Integrations & CRM**: Linear, Jira, Notion, GitHub PR workflows, Slack, Stripe
   - 🔬 **Science & Bio**: AlphaFold, UniProt, BLAST, PDB, chemistry, genetics

3. **Handle Match**:
   - If in **`auto`** mode:
     ```
     ⚡ [remember-me] Activated skill: <skill-name>
     ```
     Read its `SKILL.md` to adopt its rules, constraints, and instructions.
   - If in **`whisper`** mode:
     ```
     💡 [remember-me] I noticed your task relates to <skill-name>. Would you like me to follow its workflow?
     ```
     Wait for user approval.

4. **No Match**:
   - If no specialized skill matches the request, proceed directly with standard expert coding and reasoning.

---

## 🛠️ Maintenance & Self-Healing

If `SKILLS_INDEX.md` is ever missing or outdated, run the indexer engine:

```bash
python sync_skills_index.py
```

To re-install the global brain rules into any new environment:

```bash
python install.py
```
