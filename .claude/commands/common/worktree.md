---
allowed-tools: Bash
description: Create a new git worktree with automatic branch naming based on description
---

## Context

This command creates a new git worktree with automatic branch naming based on the provided description. It supports both feature and fix branch types.

## Your task

Create a new git worktree following these steps:

1. **Parse the description**: Determine if this is a feature or fix based on keywords or user specification
2. **Generate branch name**: Convert the description to a proper branch name format:
   - Feature branches: `feature/description-in-kebab-case`
   - Fix branches: `fix/description-in-kebab-case`
   - Remove special characters, convert to lowercase, replace spaces with hyphens
3. **Create worktree**: Use `git worktree add` to create the new worktree
4. **Navigate to worktree**: Change to the new worktree directory
5. **Confirm creation**: Show the user the created branch and location

## Branch naming rules

- Convert description to kebab-case (lowercase with hyphens)
- Remove special characters except hyphens
- Prefix with `feature/` for new functionality
- Prefix with `fix/` for bug fixes
- Maximum 50 characters for the branch name part

## Expected Input

The user will provide:
- A description of what they want to work on
- Optionally specify if it's a "feature" or "fix" (auto-detect if not specified)

## Expected Output

- A new git worktree created in `../datadis-[branch-name]`
- Navigation to the new worktree directory
- Confirmation message with branch name and location

## Auto-detection keywords

- **Feature keywords**: add, implement, create, new, enhance, improve
- **Fix keywords**: fix, bug, error, issue, repair, correct, resolve

## Example usage

- "add user authentication" → `feature/add-user-authentication`
- "fix login bug" → `fix/login-bug`
- "implement payment system" → `feature/implement-payment-system`
