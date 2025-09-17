---
description: Execute complete 6-phase workflow from start to finish
---
Execute complete workflow for: $ARGUMENTS

**WORKFLOW EXECUTION:**

**PHASE 1 - UNDERSTANDING:**
1. Start new session with `/start-session $ARGUMENTS`
2. Launch `requirement-understander` agent
3. Wait for completion of understanding phase

**PHASE 2 - ANALYSIS:**
1. Launch `situation-analyzer` agent
2. Agent reads: `.claude/sessions/session-[id]/1-understanding.md`
3. Agent creates: `.claude/sessions/session-[id]/2-analysis.md`

**PHASE 3 - RESEARCH:**
1. Launch `strategy-researcher` agent
2. Agent reads: understanding.md + analysis.md
3. Agent creates: `.claude/sessions/session-[id]/3-research.md`

**PHASE 4 - PLANNING:**
1. Launch `task-planner` agent
2. Agent reads: understanding.md + analysis.md + research.md
3. Agent creates: `.claude/sessions/session-[id]/4-tasks.md`

**PHASE 5 - EXECUTION:**
1. Read task categories from tasks.md
2. Launch appropriate executor agents in parallel:
   - `content-executor` for content-tasks
   - `research-executor` for research-tasks
   - `technical-executor` for technical-tasks
   - `data-executor` for data-tasks
   - `communication-executor` for communication-tasks
3. All executors update: `.claude/sessions/session-[id]/5-execution.md`

**PHASE 6 - MEMORY UPDATE:**
1. Launch `memory-bank-updater` agent
2. Agent reads all session files
3. Agent updates project memory files

**EXECUTION RULES:**
- Each phase waits for previous phase completion
- Phase 5 can run executors in parallel
- Session state updated after each phase
- Active context maintained throughout

**FINAL RESULT:**
Complete workflow execution with all deliverables and updated project memory.