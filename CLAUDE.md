# Datadis Python SDK

## Project Overview
A Python SDK for accessing Spanish electricity consumption data through the Datadis platform. The project provides both programmatic API access and CLI tools for energy data analysis.

## Optimized 6-Phase Workflow

### Workflow Architecture
```
UNDERSTAND → ANALYZE → RESEARCH → PLAN → EXECUTE → MEMORY
```

### Core Principles
- **Single Responsibility**: Each agent has ONE specific job
- **Context Handoff**: Each phase reads previous outputs, creates new output
- **Parallel Execution**: Phase 5 can run multiple executors simultaneously
- **Session Persistence**: Complete context preservation across sessions
- **Incremental Progress**: Resume from any phase without losing context

### Workflow Agents

**Phase 1 - Understanding:**
- `requirement-understander`: Clarifies WHAT is wanted
- Output: `1-understanding.md`

**Phase 2 - Analysis:**
- `situation-analyzer`: Assesses current state vs requirements
- Input: understanding.md
- Output: `2-analysis.md`

**Phase 3 - Research:**
- `strategy-researcher`: Investigates HOW to achieve requirements
- Input: understanding.md + analysis.md
- Output: `3-research.md`

**Phase 4 - Planning:**
- `task-planner`: Breaks down strategy into executable tasks
- Input: understanding.md + analysis.md + research.md
- Output: `4-tasks.md`

**Phase 5 - Execution:**
- `content-executor`: Documentation, writing, communication
- `research-executor`: Deep investigation, data gathering
- `technical-executor`: Development, configuration, scripting
- `data-executor`: Analysis, processing, transformation
- `communication-executor`: Reports, presentations, stakeholder communication
- Input: `4-tasks.md`
- Output: `5-execution.md` (all executors contribute)

**Phase 6 - Memory:**
- `memory-bank-updater`: Updates project knowledge
- Input: All session files
- Output: Updated `.claude/memory/` files

### Session Management

**Session Structure:**
```
.claude/sessions/session-[timestamp]/
├── session-state.md          # Session tracking
├── 1-understanding.md        # Requirements
├── 2-analysis.md             # Current state analysis
├── 3-research.md             # Strategy research
├── 4-tasks.md                # Task breakdown
└── 5-execution.md            # Execution results
```

**Context Files:**
```
.claude/context/
├── active-session.md         # Current session info
├── session-template.md       # Template for new sessions
└── agent-handbook.md         # Agent workflow guide
```

### Workflow Commands

**Core Commands:**
- `/full-flow [description]` - Complete 6-phase workflow
- `/start-session [description]` - Initialize new session
- `/list-sessions` - Show all available sessions

**Phase Commands:**
- `/understand [request]` - Phase 1 only
- `/analyze` - Phase 2 only
- `/research` - Phase 3 only
- `/plan` - Phase 4 only
- `/execute [type|all]` - Phase 5 only
- `/update-memory` - Phase 6 only

**Resume Commands:**
- `/resume-from [phase]` - Resume from specific phase
- `/continue-session [id]` - Continue existing session

### Optimization Benefits

**Context Efficiency:**
- Each agent reads only required inputs
- Minimal context loaded per phase
- Progressive context building
- Clean handoffs between phases

**Parallel Execution:**
- Phase 5 executors run simultaneously
- Task types isolated for parallel work
- No context conflicts between executors

**Session Persistence:**
- Resume from any point without data loss
- Complete audit trail of decisions
- Reusable session patterns
- Context preservation across time

**Memory Management:**
- Incremental memory updates
- Project knowledge accumulation
- Pattern recognition and reuse
- Continuous learning from sessions

### Execution Rules

**Main Agent Responsibilities:**
- Only the main agent implements workflow orchestration
- Subagents are specialists with single responsibilities
- Session state maintained by main agent
- Context handoffs managed centrally

**Agent Constraints:**
- Agents never execute outside their phase
- Input/output files strictly defined
- No cross-phase interference
- Clear separation of concerns

**Quality Standards:**
- Each phase builds on previous phases
- Clear references to predecessor outputs
- Consistent formatting across all outputs
- Progress tracking in session state
- Audit trail of all decisions

This optimized workflow reduces token usage, enables parallel execution, maintains clean context, and provides complete session persistence for maximum efficiency and resumability.