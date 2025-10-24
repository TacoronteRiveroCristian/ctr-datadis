# Historical Project Patterns

## Recurring Errors (Based on Changelog)

### 1. CUPS Validation (Central Theme)
- **v0.4.1**: Completely removed CUPS validation
- **v0.4.2**: Restored CUPS validation due to problems
- **Lesson**: API needs basic local validation before sending
- **Current decision**: Validate format in SDK, existence in API

### 2. Monthly Dates (Persistent Problem)
- **v0.3.1**: V1 date validation fix (only YYYY/MM)
- **v0.4.0**: V2 date validation implementation
- **Pattern**: Users try daily format (YYYY/MM/DD)
- **Solution**: Strict validation + clear error messages

### 3. V1 and V2 Compatibility
- **v0.2.0**: V2 client introduction
- **v0.4.0**: Unify V1/V2 date behavior
- **Pattern**: Inconsistencies between versions cause confusion
- **Principle**: Maintain similar behavior between versions

### 4. Testing and Quality
- **Evolution**: 74 tests → 298 tests → 343 tests
- **Problem**: Tests didn't cover edge cases sufficiently
- **Solution**: Mandatory test-first development

## Successful Architectural Decisions

### 1. Pydantic for Validation
- **Since v0.1.0**: Type-safe Pydantic models
- **Result**: Robust automatic validation
- **Expansion**: Complete Dict → Pydantic migration

### 2. Flexible Parameters (v0.3.0)
- **Problem**: Users passed datetime instead of string
- **Solution**: Automatic type converters
- **Result**: Better development experience

### 3. V2 Client for Advanced Functionality
- **Clear separation**: V1 basic, V2 advanced
- **Benefit**: Don't break V1 compatibility

## Identified Anti-Patterns

### 1. Breaking Changes Without Justification
- **v0.4.1 error**: Remove CUPS validation completely
- **Consequence**: Users sending invalid CUPS to API
- **Lesson**: Breaking changes require impact analysis

### 2. Inconsistency Between Versions
- **Historical problem**: V1 and V2 with different behaviors
- **Solution**: Unify basic behaviors

### 3. Insufficient Tests for Edge Cases
- **Pattern**: Production problems not detected in tests
- **Solution**: Exhaustive tests for validations
