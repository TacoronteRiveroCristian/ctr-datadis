---
description: Execute only the planning phase (Phase 4)
---
Execute planning phase for current session.

**PREREQUISITES:**
- Active session must exist
- Phases 1-3 must be completed
- Files must exist: understanding.md + analysis.md + research.md

**EXECUTION:**
1. Launch `task-planner` agent
2. Agent reads: understanding.md + analysis.md + research.md
3. Agent creates: `.claude/sessions/session-[id]/4-tasks.md`
4. Update session state to mark phase 4 complete

**NEXT STEPS:**
- Use `/execute [task-type]` to execute specific tasks
- Use `/execute all` to execute all task types