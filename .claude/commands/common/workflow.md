---
allowed-tools: Task
description: Execute a complete analysis and execution workflow using three specialized agents in sequence, then launch tasks in parallel
---

## Context

You will execute a comprehensive workflow that processes a proposal or requirement through multiple analysis phases:

## Your task

Execute the following workflow sequentially using the specified agents, then launch all generated tasks in parallel:

### Phase 1: Context Analysis
Use the **context-analyst** agent to:
- Analyze the provided proposal/requirement
- Generate a comprehensive context analysis document
- Identify key stakeholders, constraints, and success criteria

### Phase 2: Solution Research
Use the **solution-researcher** agent to:
- Research and generate multiple alternative solutions
- Provide structured analysis with trade-offs and comparisons
- Recommend the most suitable approach based on the context analysis

### Phase 3: Execution Planning
Use the **execution-planner** agent to:
- Convert the recommended solution into actionable execution plans
- Create detailed checklists with dependencies and timelines
- Generate proposal files and task breakdowns

### Phase 4: Parallel Task Execution
Launch all generated tasks from the execution planning phase in parallel using multiple Task tool calls in a single message to maximize performance.

## Expected Input

The user will provide a proposal, requirement, or problem statement that needs to be analyzed and executed.

## Expected Output

- Context analysis document
- Alternative solutions with recommendations
- Detailed execution plans and checklists
- Parallel execution of all identified tasks
