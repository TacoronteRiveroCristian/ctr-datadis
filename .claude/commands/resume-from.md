---
description: Resume workflow from specific phase
---
Resume workflow from phase: $ARGUMENTS

**VALID PHASES:**
- 1 = understanding
- 2 = analysis
- 3 = research
- 4 = planning
- 5 = execution
- 6 = memory

**PREREQUISITES:**
- Active session must exist
- All previous phases must be completed
- Required input files must exist

**EXECUTION:**

**FROM PHASE 2 (analysis):**
- Requires: 1-understanding.md
- Execute: `/analyze`

**FROM PHASE 3 (research):**
- Requires: 1-understanding.md + 2-analysis.md
- Execute: `/research`

**FROM PHASE 4 (planning):**
- Requires: 1-understanding.md + 2-analysis.md + 3-research.md
- Execute: `/plan`

**FROM PHASE 5 (execution):**
- Requires: 4-tasks.md
- Execute: `/execute all`

**FROM PHASE 6 (memory):**
- Requires: All session files
- Execute: memory-bank-updater agent

**VALIDATION:**
1. Check active session exists
2. Verify all prerequisite files exist
3. Update session state to target phase
4. Execute appropriate command/agent