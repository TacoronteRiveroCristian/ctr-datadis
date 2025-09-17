---
argument-hint: [num_commits] [memory_name?]
description: Intelligently analyze recent commits and auto-update appropriate memories.
---

# Smart Commit Analysis for Memory Update

## Phase 1: Initial Analysis
```bash
# Get commit overview with file stats
git log -n $1 --oneline --numstat --format="%h %s"
```

## Phase 2: Intelligent Filtering

**Priority Files (always analyze):**
- `*.py` (core code)
- `pyproject.toml`, `requirements.txt` (dependencies)
- `CLAUDE.md`, `README.md` (project docs)
- `Dockerfile`, `.github/workflows/*` (infrastructure)

**Smart Deletion Handling:**
- Pure deletions (0 insertions): Extract reason from commit message only
- Mass deletions (>20 files): Categorize by type, don't read content
- Doc cleanups: "Eliminated X obsolete documentation files"

**Mass Operation Detection:**
```bash
# If >50 files changed, use summary approach
git show --stat COMMIT | head -3
```

**Auto Memory Selection Logic:**
If $2 is provided, use that memory. Otherwise, auto-select based on commit patterns:
- `feat:`, `add:` → "recent_features" memory
- `fix:`, `bug:` → "recent_fixes" memory
- `refactor:`, `clean:`, `remove:` → "architecture_changes" memory
- `deps:`, `bump:`, `update:` dependency files → "project_dependencies" memory
- Mass operations (>20 files) → "project_updates" memory
- Mixed commits → "recent_changes" memory (default)

## Phase 3: Selective Deep Analysis
Only for structural changes and key files (<20 files):
```bash
git show --name-only COMMIT_HASH
git diff HEAD~1..HEAD --stat
```

## Output Format:
```
feat: nueva API endpoint - core files: client/v2.py, models/response.py
clean: removed 15 legacy .md files - documentation cleanup
fix: authentication bug - modified: client/base.py (auth flow)
deps: updated poetry.lock - dependency updates
```

**Auto-Update Process:**
1. If $2 specified: Update that memory
2. If $2 empty: Analyze commit types and auto-select appropriate memory
3. Update selected memory with categorized summary focusing on architectural impact and structural changes
4. Report which memory was updated and why

**Usage Examples:**
- `/serena/setup/update_memory_from_commits 5` → Auto-selects memory based on commit analysis
- `/serena/setup/update_memory_from_commits 3 recent_features` → Forces update to "recent_features"
