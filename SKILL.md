---
name: remember-me
description: "MANDATORY: Evaluated on ANY coding, design, debugging, database, architecture, or testing task. Checks the inline installed skills catalog in your system rules to recall and activate matching specialized workflows. Modes: auto (default), whisper, sync. Also trigger on /remember-me, /remember-me-auto, /remember-me-whisper, 'remember skills', 'recall skills', or 'what skills do you have'."
argument-hint: "[auto|whisper|sync]"
license: MIT
---

# Remember-Me: Autonomous Skill Recall Reflex (v2)

Modern AI coding agents (Antigravity, Claude Code, Codex, Cursor) frequently suffer from the **Skill Discoverability Problem**: when users install dozens or hundreds of specialized skills, the agent's prompt context budget truncates or drops them. The agent literally forgets that specialized workflows exist.

**Remember-Me v2** is an inline cognitive reflex that solves this by embedding an ultra-compact, categorized catalog directly inside the agent's system prompt and rules—eliminating per-turn file I/O and saving over 70% in token consumption.

---

## ⚡ Modes of Operation

| Mode | Trigger / Switch | Behavior |
| :--- | :--- | :--- |
| **`auto`** *(Default)* | `/remember-me auto`<br>`/remember-me-auto` | **Autonomous Activation**: The agent announces `⚡ [remember-me] Activated skill: <skill-name>`, loads `SKILL.md`, and follows its exact workflows immediately. |
| **`whisper`** | `/remember-me whisper`<br>`/remember-me-whisper` | **Confirmation-First**: The agent announces `💡 [remember-me] I noticed this task relates to '<skill-name>'. Would you like me to follow its specialized workflow?` and waits for user confirmation before proceeding. |
| **`sync`** | `/remember-me sync` | Runs the automated indexer script (`python sync_skills_index.py`) to refresh the inline catalog across all agent rules when new skills are installed. |

---

## 🧠 Step 0: The Pre-Flight Reflex

Before planning, scaffolding, creating code, or modifying architectures for any non-trivial task:

1. **Scan the Inline Catalog**:
   - Location: Embedded directly inside your system rules (`rules/remember-me.md`, `CLAUDE.md`, `AGENTS.md`, or `.cursor/rules/remember-me.mdc`).
   - Zero file I/O is required to discover skills—the index is already in context.
   - Cryptic or abstract skill names are disambiguated with parenthetical micro-hints (e.g. `grill-me (interview user requirements)`, `clarity-gate (rag verification)`, `vexor (vector code search)`).

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
   - 🛠️ **Tools & General Dev**: Development utilities, CLI tools, refactoring

3. **Handle Match**:
   - If in **`auto`** mode:
     ```
     ⚡ [remember-me] Activated skill: <skill-name>
     ```
     Read the skill's `SKILL.md` on demand to adopt its rules, constraints, and instructions.
   - If in **`whisper`** mode:
     ```
     💡 [remember-me] I noticed your task relates to '<skill-name>'. Would you like me to follow its workflow?
     ```
     Wait for user approval.

4. **No Match**:
   - If no specialized skill matches the request, proceed directly with standard expert coding and reasoning without hesitation.

---

## 🛠️ Maintenance & Self-Healing

When new skills, plugins, or tools are installed or removed, refresh all agent rules:

```bash
python sync_skills_index.py
```

To deploy or reinstall Remember-Me across Antigravity, Claude Code, Codex, and Cursor:

```bash
python install.py
```
