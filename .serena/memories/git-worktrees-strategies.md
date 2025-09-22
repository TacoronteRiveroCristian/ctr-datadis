# Git Worktrees and Advanced Strategies

## Git Worktrees for Datadis SDK

### Ideal Use Cases
```bash
# Work on feature while maintaining develop
git worktree add ../datadis-feature feature/nueva-funcionalidad

# Testing in production while developing
git worktree add ../datadis-hotfix hotfix/cups-validation

# Documentation in parallel
git worktree add ../datadis-docs docs/update-sphinx
```

### Typical Worktree Structure
```
datadis/                    # Main worktree (develop)
├── datadis_python/
├── tests/
└── docs/

../datadis-feature/         # Feature branch
├── datadis_python/
└── tests/

../datadis-docs/           # Documentation
└── docs/
```

## Branch Strategy (From Project)

### Main Branches
- **main**: Stable production (v0.4.2)
- **develop**: Active development
- **feature/**: New features
- **hotfix/**: Urgent fixes
- **docs/**: Documentation updates

### Workflow with Worktrees
1. **Main develop**: `datadis/` (develop branch)
2. **Feature in parallel**: `../datadis-feature/`
3. **Independent tests**: Each worktree can run tests
4. **Merge**: From feature worktree → develop

## Advantages for This Project

### Parallel Testing
- Run tests in develop while coding feature
- Verify compatibility between versions
- Background regression tests

### Sphinx Documentation
- Generate docs in separate worktree
- Don't interfere with active development
- Independent documentation preview

### Critical Hotfixes
- CUPS validation, monthly dates require quick fixes
- Hotfix worktree without affecting ongoing development

## Project-Specific Commands
```bash
# Setup worktree for new feature
git worktree add ../datadis-cups-fix feature/cups-validation-fix
cd ../datadis-cups-fix
poetry install

# Parallel testing
cd ../datadis-cups-fix && poetry run pytest
cd ../datadis && poetry run pytest --coverage
```
