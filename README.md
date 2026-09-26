# 🧠 Remember-Me

> **Autonomous Skill Discovery & Recall Reflex for AI Coding Agents**  
> *Never let your agent forget a specialized skill again.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)]()
[![Compatible with: Antigravity | Claude Code | Cursor | Codex](https://img.shields.io/badge/Agents-Antigravity%20%7C%20Claude%20Code%20%7C%20Cursor%20%7C%20Codex-purple.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)]()

---

## 💥 The Problem: Why Agents Forget Skills

Modern AI coding agents (such as **Antigravity**, **Claude Code**, **Codex**, or **Cursor**) allow users to install custom skills and workflows. However, as your library grows past 30–50 skills, a major bottleneck occurs:

1. **Context Window Pruning**: The agent runtime attempts to inject all skill summaries into the system prompt. When the token budget overflows, **the runtime silently truncates and excludes the rest**. (In large setups, over 80% of skills are dropped before the AI even reads your message!).
2. **Attentional Dilution**: With dozens of skill descriptions cluttering the prompt, LLM semantic attention spreads thin, leading the agent to overlook specialized workflows and default to generic answers.
3. **The Discovery Trap**: If the user doesn't remember the exact name of the skill to invoke it manually, the agent never uses it.

---

## ⚡ The Solution: The "Library Catalog" Reflex

**Remember-Me** solves this through a **Two-Tier Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. The Brain Rule (Involuntary Reflex)                      │
│    A permanent rule loaded in every turn's system prompt    │
│    instructs the agent: "Always check SKILLS_INDEX.md"     │
├─────────────────────────────────────────────────────────────┤
│ 2. The Skills Index (Compact Knowledge Catalog)             │
│    A categorized markdown catalog (~15 tokens per skill)    │
│    allowing 1,000+ skills to be indexed in under 3k tokens  │
├─────────────────────────────────────────────────────────────┤
│ 3. Automated Indexer & Bootstrapper                         │
│    A lightning-fast 2-second Python engine that crawls      │
│    skill directories and keeps the catalog in sync          │
└─────────────────────────────────────────────────────────────┘
```

Instead of drowning the model's context with 1,000 full skill definitions, the agent glances at **one compact table** and pulls only the exact skill needed for your task in milliseconds.

---

## 🚀 Quick Start (One-Click Install)

Clone the repository and run the self-bootstrapper:

```bash
git clone https://github.com/stockfishZ/Remember-Me.git
cd remember-me
python install.py
```

### What `install.py` Does Automatically:
1. Detects your installed agents (**Antigravity**, **Claude Code**, etc.).
2. Copies `SKILL.md` to your agent's skills directory.
3. Injects the behavioral rule into `rules/remember-me.md` and/or `CLAUDE.md`.
4. Crawls all installed skills and compiles your initial `SKILLS_INDEX.md`.

---

## 🎮 Modes of Operation

Remember-Me features two primary operational modes:

### 1. `auto` Mode (Default)
The agent autonomously identifies relevant skills, announces them, and adopts their workflows immediately:
```text
User: "Help me write a high-performance ClickHouse migration."
Agent: "⚡ [remember-me] Activated skill: cc-skill-clickhouse-io
       Reading specialized guidelines..."
```

### 2. `whisper` Mode
The agent acts with a confirmation gate, suggesting matching skills before loading them:
```text
User: "Help me write a high-performance ClickHouse migration."
Agent: "💡 [remember-me] I noticed this task relates to 'cc-skill-clickhouse-io'.
       Would you like me to follow its specialized workflow?"
```

### Switching Modes
You can switch modes anytime directly in chat or via slash commands:
- `/remember-me auto` (or `/remember-me-auto`)
- `/remember-me whisper` (or `/remember-me-whisper`)
- `/remember-me sync` (refresh catalog)

---

## 🗂️ How SKILLS_INDEX.md is Organized

The indexer categorizes skills into clear domains for instant matching:

| Domain | Example Skills Covered |
| :--- | :--- |
| 🛡️ **Security & Pentesting** | OWASP, XSS, IDOR, IAM hardening, threat modeling |
| 🗄️ **Database & Storage** | PostgreSQL, Redis, ClickHouse, Prisma, migrations |
| 🚀 **Cloud & DevOps** | Docker, Kubernetes, Terraform, AWS, Azure, GCP, CI/CD |
| 🤖 **AI, Agents & LLM** | LangChain, CrewAI, RAG, prompt engineering, evals |
| 🧪 **Testing & QA** | TDD workflows, Playwright, Jest, benchmarking |
| ⚙️ **Backend & API** | Node.js, FastAPI, Go, Rust, .NET, GraphQL, DDD |
| 🌐 **Frontend & UI** | React, Tailwind, Next.js, animations, design tokens |
| 💼 **Integrations & CRM** | GitHub PRs, Linear, Jira, Slack, Notion, Stripe |
| 🔬 **Science & Domain** | Bio, genomics, audio/transcription, game dev |
| 🛠️ **Tools & General** | CLI helpers, shell scripting, scrapers, documentation |

---

## 🔄 Refreshing the Catalog

Whenever you install new skills or plugins, refresh the index with:

```bash
python sync_skills_index.py
```
*(Or simply tell your agent: `/remember-me sync`)*

---

## 🧩 Compatibility

| Agent Platform | Integration Method | Supported? |
| :--- | :--- | :---: |
| **Antigravity (Gemini)** | Native Global Rule + Skill package | ✅ Yes |
| **Claude Code** | Global `CLAUDE.md` + Skills directory | ✅ Yes |
| **Cursor IDE** | `.cursorrules` / `.cursor/rules/` | ✅ Yes |
| **Codex / Open-Source CLI** | `AGENTS.md` standard | ✅ Yes |

---

## 📄 License

MIT License. Free to use, modify, and distribute.
