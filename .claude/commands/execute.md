---
description: Execute tasks from planning phase (Phase 5)
---
Execute tasks for: $ARGUMENTS

**PREREQUISITES:**
- Active session must exist
- Phases 1-4 must be completed
- File must exist: `.claude/sessions/session-[id]/4-tasks.md`

**EXECUTION OPTIONS:**

**SPECIFIC TASK TYPE:**
If $ARGUMENTS = content|research|technical|data|communication:
- Launch specific executor agent
- Execute only tasks of that type
- Update execution.md with results

**ALL TASKS:**
If $ARGUMENTS = all:
- Launch all relevant executor agents in parallel:
  - `content-executor` for content-tasks
  - `research-executor` for research-tasks
  - `technical-executor` for technical-tasks
  - `data-executor` for data-tasks
  - `communication-executor` for communication-tasks
- All agents update: `.claude/sessions/session-[id]/5-execution.md`

**EXECUTION:**
1. Read task categories from tasks.md
2. Launch appropriate executor(s)
3. Executors update execution results
4. Update session state to mark phase 5 complete

**NEXT STEPS:**
- Use `/update-memory` to complete phase 6