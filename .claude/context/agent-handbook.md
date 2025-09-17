# Agent Workflow Handbook

## Workflow Overview
```
UNDERSTAND → ANALYZE → RESEARCH → PLAN → EXECUTE → MEMORY
```

## Phase Input/Output Chain

### Phase 1: Understanding
- **Agent**: requirement-understander
- **Input**: User request
- **Output**: `.claude/sessions/session-[id]/1-understanding.md`
- **Next**: situation-analyzer reads understanding

### Phase 2: Analysis
- **Agent**: situation-analyzer
- **Input**: `.claude/sessions/session-[id]/1-understanding.md`
- **Output**: `.claude/sessions/session-[id]/2-analysis.md`
- **Next**: strategy-researcher reads understanding + analysis

### Phase 3: Research
- **Agent**: strategy-researcher
- **Input**: understanding.md + analysis.md
- **Output**: `.claude/sessions/session-[id]/3-research.md`
- **Next**: task-planner reads understanding + analysis + research

### Phase 4: Planning
- **Agent**: task-planner
- **Input**: understanding.md + analysis.md + research.md
- **Output**: `.claude/sessions/session-[id]/4-tasks.md`
- **Next**: executors read tasks.md

### Phase 5: Execution
- **Agents**: content/research/technical/data/communication-executor
- **Input**: `.claude/sessions/session-[id]/4-tasks.md`
- **Output**: `.claude/sessions/session-[id]/5-execution.md`
- **Next**: memory-bank-updater reads all session files

### Phase 6: Memory
- **Agent**: memory-bank-updater
- **Input**: All session files
- **Output**: Updated `.claude/memory/` files

## Agent Responsibilities

### Single Responsibility Rule
Each agent has ONE job:
- **requirement-understander**: Clarify WHAT is wanted
- **situation-analyzer**: Assess current state vs requirements
- **strategy-researcher**: Find HOW to achieve requirements
- **task-planner**: Break down strategy into tasks
- **executors**: Execute specific task types
- **memory-bank-updater**: Update project knowledge

### Context Handoff Rules
1. Always read your required input files
2. Only write to your designated output file
3. Reference previous phases in your output
4. Never skip reading predecessor outputs
5. Update session state when done

## File Naming Convention
- Session folder: `session-[timestamp]`
- Phase files: `[phase-number]-[phase-name].md`
- Example: `session-20240101-120000/2-analysis.md`

## Quality Standards
- Each phase builds on previous phases
- Clear references to predecessor outputs
- Specific, actionable content
- Consistent formatting across phases
- Progress tracking in session state