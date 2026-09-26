# Remember-Me: Skill Recall Reflex (Claude Code Directive)

## Instructions for Claude Code
Add the following snippet to your `~/.claude/CLAUDE.md` or project `CLAUDE.md`:

```markdown
## Remember-Me Skill Recall Reflex

Before planning, scaffolding, or writing code for any non-trivial task (features, architecture, bug fixes, testing, security, or migrations):
1. Check `SKILLS_INDEX.md` (in ~/.claude/ or ~/.gemini/config/ or workspace root) for matching skills or domain workflows.
2. If a matching skill is found:
   - Default (`auto` mode): Announce `⚡ [remember-me] Activated skill: <skill-name>`, read its `SKILL.md`, and apply its guidelines.
   - If user requested `whisper` mode: Ask confirmation before loading the skill.
3. If no matching skill is found, proceed normally.
4. User may trigger `/remember-me [auto|whisper|sync]`.
```
