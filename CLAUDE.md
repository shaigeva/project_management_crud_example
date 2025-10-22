# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The project follows the specification in the `docs/spec/` directory, where the central spec is `docs/spec/main_spec.md`.
The technical specification is in the `docs/tech_spec/` directory, where the central technical spec is `docs/tech_spec/high_level_architecture.md`.

**CRITICAL**: Read `docs/spec/how_to_write_specs.md` to understand the philosophy of product behavior vs technical details.

## Specification-Driven Workflow

**CRITICAL**: Read `docs/spec/how_to_write_specs.md` for detailed guidance on writing specs and tests.

### Core Principle

**Specifications define ALL behavior before implementation.**
- Product behavior (externally observable) is PRIMARY
- Tests verify spec behaviors through external API
- See `docs/spec/how_to_write_specs.md` for philosophy and examples

### Workflow Overview

#### Phase 1: Specification & Planning (COLLABORATIVE with user)
**What**: Update specs, create task lists, decide what to implement
**Who**: You work WITH the user to define requirements and plan tasks

1. **Update specifications** in `docs/spec/` (see how_to_write_specs.md for format)
2. **Show specs to user for review** - DO NOT commit specs without user approval
3. **Get user approval** before committing spec changes
4. **Create task list** in `docs/tasks/current_task_list.md` referencing spec requirements
5. **Show task list to user for review** - DO NOT commit task lists without user approval
6. **Discuss and agree** on what to implement next

**CRITICAL**: All specification and task list changes require user review and approval BEFORE committing.

#### Phase 2: Implementation (AUTONOMOUS after user approval)
**What**: Implement tasks to completion
**Who**: User tells you to implement tasks, you execute autonomously until done

**See `docs/how_to_implement_tasks.md` for detailed implementation process.**

**Key rules:**
- Get behavior requirements from SPEC files, not task list
- Implement tasks that cover related requirements together if makes sense
- Each task MUST cover ALL its requirements completely (no partial implementations)
- Write comprehensive tests: API, repository, utilities, domain logic
- Use standardized progress messages (see task implementation guide)
- After each task completion, ask user for approval to commit

#### Phase 3: Completion & Archival
When ALL tasks are done:
- Archive task list to `docs/tasks/archive/`
- Update feature status in main spec
- Clear current task list

## Implementation Details

### How to Implement Each Task

**Work through these steps:**

1. **Plan** - Read spec requirements. Design tests. Check if existing tests need updates.
2. **Implement** - Write code and tests together covering ALL spec scenarios.
3. **Validate** - Run `./devtools/run_all_agent_validations.sh` until zero errors/warnings.
🚨 **ZERO TOLERANCE** 🚨
- ZERO test failures, linting errors, type errors, warnings

**When validation fails:**
1. Check spec first - verify correct behavior
2. If code is wrong → fix code to match spec
3. If test is wrong → verify against spec, then fix test
4. Never change tests just to make them pass

**✅ ONLY 2 ACCEPTABLE OUTCOMES ✅**
- All tests and validations pass
- You've tried to fix the errors and failed (then tell the user)

4. **Update status** - Mark task ✅ and requirements ✅ in specs.
5. **Commit** - Ask user for approval to commit.



**Rule**: Both code AND tests must match spec.

### Commit Message Format

```
[Short title]

[One line summary]

🤖 Generated with Claude Code
```

## Core Development Principles
- **No Layer-Based Changes**. Complete capabilities only - DO NOT implement multiple distinct capabilities in the same change. DO implement a capability and all its tests before continuing to the next capability.
- **Complete capabilities only** - No partial implementations
- **Validation-driven** - Every change must pass all validations
- **Test behaviors, not implementation** - Focus on externally observable behavior
- **Small parts principle** -
Prefer breaking down functionality into small capabilities that are individually testable.
In addition to the external API-level tests, also create tests for the smaller capabilities.
For example, a serialization and deserialization capability based on the model type is individually testable.
- **Before committing** - All new behaviors have comprehensive tests

### Testing Guidelines
See `tests/CLAUDE.md` and `docs/spec/how_to_write_specs.md`
