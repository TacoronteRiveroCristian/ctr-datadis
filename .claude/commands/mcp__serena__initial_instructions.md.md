# Serena Project Onboarding Command

## Overview
Perform comprehensive onboarding for the Apuestas Personales betting app project. This command initializes Serena's understanding of the codebase, creates semantic memories, and establishes a foundation for future code analysis and searches.

## Primary Tasks

1. **Project Analysis & Onboarding**
   - Activate the app-mobile-betting project in Serena
   - Perform initial onboarding to analyze codebase structure
   - Identify and catalog key architectural components

2. **Memory Creation for Core Components**
   Create semantic memories for:
   - Project overview and technology stack
   - React Native + Expo app architecture
   - Firebase backend services integration
   - Authentication and user management flows
   - Betting system core logic (creation, participation, settlement)
   - Real-time data synchronization patterns
   - Virtual points economy and transaction handling
   - Push notification system
   - Cross-platform development patterns

   **IMPORTANT**: Memories should contain instructions, patterns, and pseudocode only - NO actual code snippets. Focus on architectural guidance, best practices, and implementation approaches rather than specific code examples.

3. **Code Structure Analysis**
   Map and memorize:
   - Feature-based architecture organization
   - Shared types and validation schemas
   - Custom hooks patterns
   - Component library structure
   - Firebase Cloud Functions organization
   - Test structure and patterns

4. **Development Workflow Patterns**
   Document and store:
   - Build and deployment processes
   - Local development setup with emulators
   - Testing strategies (unit, integration, e2e)
   - Code quality and linting configurations

   **NOTE**: Focus on commands, processes, and workflow instructions rather than implementation details.

## Expected Serena Actions

```bash
# 1. Activate project
mcp__serena__activate_project: /home/cristiantr/GitHub/app-mobile-betting

# 2. Check if onboarding was performed
mcp__serena__check_onboarding_performed

# 3. Perform comprehensive onboarding
mcp__serena__onboarding

# 4. Create specific memories for core domains
mcp__serena__write_memory: project_architecture
mcp__serena__write_memory: firebase_integration_patterns
mcp__serena__write_memory: betting_business_logic
mcp__serena__write_memory: authentication_flows
mcp__serena__write_memory: real_time_data_patterns
mcp__serena__write_memory: cross_platform_components
mcp__serena__write_memory: testing_strategies
mcp__serena__write_memory: development_commands

# 5. Analyze project structure
mcp__serena__get_symbols_overview
mcp__serena__list_dir: apps/mobile-web/src
mcp__serena__list_dir: functions/src
mcp__serena__list_dir: shared
```

## Success Criteria

After execution, Serena should have:
- Complete project onboarding performed
- 8+ semantic memories created covering all major domains
- Symbols overview generated for quick navigation
- Directory structure mapped and indexed
- Ready for semantic code searches and analysis

## Usage Notes

- This command should be run once when setting up the project
- Re-run if major architectural changes are made
- Memories will enable fast semantic searches for future development tasks
- Use `mcp__serena__list_memories` to verify all memories were created successfully

## Project Context

This is a cross-platform React Native + Expo virtual betting application with:
- TypeScript for type safety
- Firebase for backend services (Firestore, Auth, Functions, Storage)
- Virtual points economy (no real money)
- Real-time bet participation and updates
- Cross-platform support (iOS, Android, Web)
