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

**Process:**
1. **Create/update specifications** in `docs/spec/` (see how_to_write_specs.md for format)
2. **Show specs to user** - Display the changes/new content
3. **Wait for user approval** - User reviews and may request changes
4. **After user approves**: Commit the spec changes
5. **Create SHORT task list** in `docs/tasks/current_task_list.md`
   - Task list should be BRIEF (see example in current_task_list.md.EXAMPLE)
   - Each task: brief description + which requirements it implements
   - NO detailed implementation plans (those come during task implementation)
   - NO test specifications (those come during task planning phase)
6. **Show task list to user** - Display the task list
7. **Wait for user approval** - User reviews and may request changes
8. **After user approves**: Commit the task list
9. **Discuss and agree** on what to implement next

**🚨 CRITICAL RULE 🚨**
- **NEVER commit specs or task lists without explicit user approval**
- **ALWAYS show changes first, wait for approval, THEN commit**
- This applies to ALL files in Phase 1 (specs, task lists, documentation)

**Task List Guidelines:**
- Keep tasks SHORT and HIGH-LEVEL
- Reference spec requirements (REQ-XXX-YYY)
- Describe WHAT to implement, not HOW
- Detailed planning happens during implementation (in task_implementation_plan.md)

#### Phase 2: Implementation (AUTONOMOUS after user approval)
**What**: Implement tasks to completion
**Who**: User tells you to implement tasks, you execute autonomously until done

**See `docs/how_to_implement_tasks.md` for detailed implementation process.**

**Process for each task:**
1. Implement code and tests
2. Run validations until all pass (zero errors/warnings)
3. Update task and requirement statuses
4. **Show summary** of what was implemented
5. **Ask user for approval to commit**
6. **After user approves**: Commit the changes

**Key rules:**
- Get behavior requirements from SPEC files, not task list
- Implement tasks that cover related requirements together if makes sense
- Each task MUST cover ALL its requirements completely (no partial implementations)
- Write comprehensive tests: API, repository, utilities, domain logic
- Use standardized progress messages (see task implementation guide)

**🚨 COMMIT RULE 🚨**
- **NEVER commit implementation without asking user first**
- **ALWAYS: complete task → show summary → ask approval → THEN commit**

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
5. **Request commit approval** - Show what was done, ask user "Ready to commit?"
6. **After approval** - Commit with appropriate message.



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
