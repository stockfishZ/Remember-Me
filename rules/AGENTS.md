# Remember-Me: Skill Recall Reflex (Codex / AGENTS.md Directive)

## Instructions for Codex / Open-Source CLI Agents
Add the following block to your project's `AGENTS.md` or global `~/.codex/AGENTS.md` / `~/.agents/AGENTS.md` (or run `python install.py` / `python sync_skills_index.py` to auto-inject and keep updated):

```markdown
<!-- REMEMBER-ME-START -->
## Remember-Me Skill Recall Reflex

When your task involves a specialized domain and no obvious skill is already loaded,
scan the index below and read the matching skill's `SKILL.md` before proceeding.

- **`auto` mode (Default)**: Announce `⚡ [remember-me] Activated skill: <skill-name>`, load its `SKILL.md`, and follow its workflows.
- **`whisper` mode**: Ask confirmation before loading: `💡 [remember-me] I noticed this task relates to '<skill-name>'. Would you like me to follow its workflow?`
- **No match**: Proceed normally without delay.
- **Trivial tasks**: Skip this check for greetings, typo fixes, or basic one-liners.

Mode switches: `/remember-me auto` | `/remember-me whisper` | `/remember-me sync`

### Installed Skills Catalog

> Run `python sync_skills_index.py` to auto-populate the categorized inline index.
<!-- REMEMBER-ME-END -->
```
