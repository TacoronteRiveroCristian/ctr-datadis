# Session Template

## Session Info
- **Session ID**: session-[timestamp]
- **Created**: [date]
- **Status**: [active/completed/paused]
- **Current Phase**: [1-6]

## Phase Progress
- [ ] 1. Understanding (requirement-understander)
- [ ] 2. Analysis (situation-analyzer)
- [ ] 3. Research (strategy-researcher)
- [ ] 4. Planning (task-planner)
- [ ] 5. Execution (executors)
- [ ] 6. Memory Update (memory-bank-updater)

## Context Files
- Understanding: `.claude/sessions/session-[id]/1-understanding.md`
- Analysis: `.claude/sessions/session-[id]/2-analysis.md`
- Research: `.claude/sessions/session-[id]/3-research.md`
- Tasks: `.claude/sessions/session-[id]/4-tasks.md`
- Execution: `.claude/sessions/session-[id]/5-execution.md`

## Active Context
- **Current Phase**: [phase number and name]
- **Next Agent**: [agent to run next]
- **Input File**: [file for next agent to read]
- **Output File**: [file for next agent to write]

## Session Notes
[Any important notes or decisions made during the session]