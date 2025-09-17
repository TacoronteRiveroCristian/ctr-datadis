---
description: Start a new workflow session with unique session ID
---
Start new workflow session for: $ARGUMENTS

**INITIALIZE SESSION:**
1. Create unique session ID: `session-$(date +%Y%m%d-%H%M%S)`
2. Create session directory: `.claude/sessions/session-[timestamp]/`
3. Copy session template to session directory as `session-state.md`
4. Update session-state.md with:
   - Session ID
   - Creation date/time
   - Request description: "$ARGUMENTS"
   - Current phase: 1 (Understanding)
   - Status: active

**UPDATE ACTIVE CONTEXT:**
Update `.claude/context/active-session.md` with:
- Current session ID
- Current phase: 1
- Status: active
- Last updated timestamp

**NEXT STEP:**
Launch `requirement-understander` agent with instructions:
- Read user request: "$ARGUMENTS"
- Create understanding document
- Save to: `.claude/sessions/session-[timestamp]/1-understanding.md`
- Update session state when complete

**SESSION TRACKING:**
The session will proceed through phases:
1. Understanding → 2. Analysis → 3. Research → 4. Planning → 5. Execution → 6. Memory

Each phase agent will read previous outputs and create their own output file.