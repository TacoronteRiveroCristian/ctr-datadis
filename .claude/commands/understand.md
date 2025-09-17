---
description: Execute only the understanding phase (Phase 1)
---
Execute understanding phase for: $ARGUMENTS

**PHASE 1 - UNDERSTANDING ONLY:**

**PREREQUISITES:**
- If no active session exists, create new session first
- If active session exists, verify we're at phase 1 or can restart

**EXECUTION:**
1. Check for active session in `.claude/context/active-session.md`
2. If no session: automatically create with `/start-session $ARGUMENTS`
3. Launch `requirement-understander` agent with instructions:
   - Process user request: "$ARGUMENTS"
   - Create detailed understanding document
   - Save to: `.claude/sessions/session-[id]/1-understanding.md`
   - Update session state to mark phase 1 complete

**OUTPUT:**
- Understanding document created
- Session state updated
- Ready for phase 2 (analysis)

**NEXT STEPS:**
- Use `/analyze` to continue to phase 2
- Use `/resume-from 2` to continue workflow
- Use `/full-flow` to complete remaining phases

**STANDALONE USE:**
This command can be used independently when you only need requirement clarification without proceeding to implementation.