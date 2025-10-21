# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The project follows the specification in the `docs/spec/` directory, where the central spec is `docs/spec/main_spec.md`.
The technical specification is in the `docs/tech_spec/` directory, where the central technical spec is `docs/tech_spec/high_level_architecture.md`.

**CRITICAL**: Read `docs/spec/how_to_write_specs.md` to understand the philosophy of product behavior vs technical details.

## Specification-Driven Workflow

### Core Principles

1. **Specifications define ALL behavior before implementation**
   - Product behavior (externally observable) is PRIMARY
   - Technical details (implementation) are SECONDARY
   - Tests verify spec behaviors, not code coverage

2. **Product Behavior First**
   - Focus on what users/external systems can observe
   - Example GOOD: "After creating project, GET returns that project"
   - Example BAD: "Project is written to database"
   - See `docs/spec/how_to_write_specs.md` for detailed guidance

3. **Status is inline**
   - No separate tracking files
   - Status lives in spec files with requirements
   - Update status when behavior is implemented and tested

### Workflow Stages

#### Stage 1: Update Specifications (Before ANY implementation)
1. Update or create spec in `docs/spec/main_spec.md` (high-level)
2. Create/update detailed spec in `docs/spec/detailed/feature_xxx_detailed_spec.md`
3. Define requirements with:
   - Unique ID: REQ-{FEATURE}-{NUMBER}
   - Scenario: When does this happen?
   - Observable Behavior: What can users verify?
   - Test Specification: Explicit tests needed (name + what it verifies)
4. All new requirements start as 🔴 Not Implemented

#### Stage 2: Create Task List from Spec
1. Create `docs/tasks/current_task_list.md`
2. Each task MUST reference specific REQ-XXX-YYY it implements
3. Break down into small tasks with clear dependencies
4. Define what tests each task requires
5. Link tasks to spec behaviors they will implement

#### Stage 3: Implement Tasks ONE AT A TIME
- Implementation MUST follow task sequence in `docs/tasks/current_task_list.md`
- **Requirements source**: Get detailed behavior requirements from the SPEC, not task list
- **Implement EXACTLY ONE task at a time - NEVER implement multiple tasks together**
- 🚨 **ONE TASK ONLY**: Even if tasks seem related, implement separately. No exceptions. No batching.
- Implementation of "one task" includes: planning, implementing code and tests, running validations, and preparing for commit

**For each task:**
1. Read spec requirements it implements
2. Implement code matching spec behaviors EXACTLY
3. Write tests covering ALL spec scenarios (see spec's "Test Specification" section)
4. Include all edge cases from spec
5. Run validations until zero errors/warnings
6. Update task status in `docs/tasks/current_task_list.md`: ⏳ → 🔄 → ✅
7. Update requirement status in spec: 🔴 → ✅
8. Ask user for approval to commit

**After completing each task (validations passing), STOP and ask for user approval before committing.**

#### Stage 4: Complete Task List and Update Specs
When ALL tasks in current_task_list.md are ✅:
1. Archive task list to `docs/tasks/archive/YYYY-MM-DD_description.md`
2. Update feature status in `docs/spec/main_spec.md`:
   - Update requirement counts (e.g., 🔴 0/8 → 🟡 4/8)
   - Change feature emoji if 100% done (🔴 → 🟡 or 🟢)
3. Delete or clear `docs/tasks/current_task_list.md`

### Status Indicators

**Requirement Status** (inline in spec files):
- 🔴 Not Implemented
- ✅ Implemented and tested
- ⚠️ Implemented incorrectly (needs fix)

**Feature Status** (in main_spec.md):
- 🔴 Not Started (0% requirements)
- 🟡 Partial (1-99% requirements)
- 🟢 Fully Implemented (100% requirements)

**Task Status** (in current_task_list.md):
- ⏳ Pending
- 🔄 In Progress
- ✅ Done

### **Commit Message Format**

Keep commit messages concise:
```
[Short title]

[One line summary of changes]

🤖 Generated with Claude Code
```
- DO NOT specify "Co-Authored-By"

Example:
```
Memory Size Tracking

Add size tracking for in-memory cache items.

🤖 Generated with Claude Code
```

### **How to implement each task**

**Work through these 3 sub-tasks sequentially:**

1. **Plan** - Read the spec for this task's requirements. Describe the behavior to implement in detail. Design tests for the new behavior. Identify if any existing tests need updates to cover modified functionality.

2. **Implement** - Write the code and all tests together. Include updates to existing tests if identified in planning.

3. **Validate and prepare** - Run `./devtools/run_all_agent_validations.sh` and fix any failures. Repeat until all validations pass (zero errors, zero warnings). Once passing, update `IMPLEMENTATION_PLAN.md` and ask user for approval to commit.

**Progress Tracking:**
- Use clear markdown comments to show progress (e.g., `## Task Plan: SQLite Connection Setup`)
- Do NOT use TodoWrite for task tracking (wastes tokens)
- Only use TodoWrite if a single task has >5 complex sub-tasks or user explicitly requests it

## Development Guidelines

### **Validation Strategy**

Run `./devtools/run_all_agent_validations.sh` during the "Validate and commit" sub-task.

🚨 **ABSOLUTE ZERO TOLERANCE POLICY** 🚨
- ZERO test failures
- ZERO linting errors
- ZERO type errors
- ZERO warnings

### **When Validation Fails**

**Critical: Think before changing tests**

When fixing validation failures, follow this process:

1. **Identify the failure** - What exactly is failing? (test, type check, lint, etc.)

2. **Check the spec first** - Before changing ANY code or test:
   - Re-read the relevant section of the spec
   - Confirm what the correct behavior should be
   - Verify your understanding matches the spec

3. **Determine the fix**:
   - If test fails because **code is wrong**: Fix the code to match spec
   - If test fails because **test expectation is wrong**: Verify against spec, then fix test
   - **Never** change test expectations just to make tests pass without re-confirming against spec

4. **Common mistake to avoid**:
   - ❌ Test fails → change test expectation → test passes → commit
   - ✅ Test fails → check spec → fix code to match spec → test passes → commit

5. **Apply fix and re-run** - Run validations again until passing

**Rule: Both code AND tests must match the spec. If validation passes and both match spec, ask user for approval to commit.**

### **🚫 FORBIDDEN PHRASES 🚫**

**NEVER SAY:**
- "Some tests are skipped but acceptable"
- "Only minor warnings remain"
- "Most tests pass"
- "Timing issues are expected"
- "This is acceptable"
- "Tests pass in isolation but fail in parallel"

**✅ ONLY 2 ACCEPTABLE OUTCOMES ✅**
- All tests and validations pass
- You've tried to fix the errors and failed (then tell the user)

## **Core Development Principles**
- **One Change = One Complete, testable Capability**
- **Validation-Driven Development** (every change must pass all validations)
- **Test-First Implementation** (behavior tests that target the API of the package are Priority 1)
- **No Layer-Based Changes**. Complete capabilities only - DO NOT implement multiple distinct capabilities in the same change. DO implement a capability and all its tests before continuing to the next capability.
- **Before committing, make sure all new or changed behaviors have tests that cover them well**

### **Small parts principle**
Prefer breaking down functionality into small capabilities that are individually testable.
In addition to the external API-level tests, also create tests for the smaller capabilities.
For example, a serialization and deserialization capability based on the model type is individually testable.

### **Testing guidelines**
See the tests/CLAUDE.md file
