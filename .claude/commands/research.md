---
description: Execute only the research phase (Phase 3)
---
Execute research phase for current session.

**PREREQUISITES:**
- Active session must exist
- Phases 1-2 must be completed
- Files must exist: understanding.md + analysis.md

**EXECUTION:**
1. Launch `strategy-researcher` agent
2. Agent reads: understanding.md + analysis.md
3. Agent creates: `.claude/sessions/session-[id]/3-research.md`
4. Update session state to mark phase 3 complete

**NEXT STEPS:**
- Use `/plan` to continue to phase 4