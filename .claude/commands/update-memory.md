---
description: Execute memory update phase (Phase 6)
---
Execute memory update for current session.

**PREREQUISITES:**
- Active session must exist
- Phase 5 (execution) must be completed
- File must exist: `.claude/sessions/session-[id]/5-execution.md`

**EXECUTION:**
1. Launch `memory-bank-updater` agent
2. Agent reads all session files:
   - 1-understanding.md
   - 2-analysis.md
   - 3-research.md
   - 4-tasks.md
   - 5-execution.md
3. Agent updates project memory files in `.claude/memory/`
4. Update session state to mark phase 6 complete
5. Mark session as completed

**FINAL RESULT:**
- Project memory updated with session learnings
- Session marked as complete
- Workflow cycle finished