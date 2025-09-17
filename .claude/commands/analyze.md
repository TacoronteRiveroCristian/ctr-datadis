---
description: Execute only the analysis phase (Phase 2)
---
Execute analysis phase for current session.

**PREREQUISITES:**
- Active session must exist
- Phase 1 (understanding) must be completed
- File must exist: `.claude/sessions/session-[id]/1-understanding.md`

**EXECUTION:**
1. Launch `situation-analyzer` agent
2. Agent reads: `.claude/sessions/session-[id]/1-understanding.md`
3. Agent creates: `.claude/sessions/session-[id]/2-analysis.md`
4. Update session state to mark phase 2 complete

**NEXT STEPS:**
- Use `/research` to continue to phase 3
- Use `/resume-from 3` to continue workflow