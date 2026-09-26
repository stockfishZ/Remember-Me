# Remember-Me: Autonomous Skill Recall Reflex

## Core Directive
Before planning, scaffolding, or implementing any non-trivial user task (architecture, feature development, bug fixes, database design, testing, security, or integrations), you **MUST** perform a **Step 0: Skill Pre-flight Check**.

Do NOT assume you must implement everything from scratch. You have specialized skills installed across the system.

## Step 0 Execution
1. Check `SKILLS_INDEX.md` (in ~/.gemini/config/, ~/.claude/, or workspace root) for skills whose domain, keywords, or triggers match the user's intent.
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
