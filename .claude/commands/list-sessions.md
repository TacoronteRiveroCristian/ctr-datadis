---
description: List all available workflow sessions
---
List all available workflow sessions.

**EXECUTION:**
1. Check `.claude/sessions/` directory for session folders
2. For each session:
   - Read session-state.md
   - Extract session info: ID, status, current phase, description
   - Show last updated timestamp
3. Display in organized table format

**OUTPUT FORMAT:**
```
Available Sessions:
ID                    | Status  | Phase | Description           | Last Updated
session-20240101-1200 | active  | 3     | API enhancement      | 2024-01-01 12:30
session-20240101-0900 | paused  | 5     | Data migration       | 2024-01-01 10:15
session-20231230-1500 | complete| 6     | Bug fix workflow     | 2023-12-30 16:00
```

**ADDITIONAL INFO:**
- Show which sessions can be resumed
- Highlight current active session
- Show phase completion status