# Copilot Agent Rules

This document provides clear and streamlined guidelines to leverage AI coding agents effectively, ensuring disciplined and structured project development without sacrificing flexibility.

## MAIN PRINCIPLES

- **Task-driven Development:**
  - Every code implementation must be directly tied to a clearly defined Task.
  - Each Task must be associated explicitly with a corresponding Specification.

- **No Untracked Implementations:**
  - No changes or features should ever be implemented without a corresponding Task and Specification. If such a case arises, immediately prompt the user to clarify or resolve the discrepancy.

- **Automated Consistency Checks:**
  - Continuously verify synchronization between code, tasks, and specifications.
  - Prompt the user proactively if inconsistencies or gaps are detected.

## Workflow

**Standard Implementation Flow:**

1. **User Request** → Clearly captures user intentions.
2. **Specification Updates** → Update `.project/specs/` accordingly.
3. **Task Creation** → Create structured tasks in `.project/tasks/`.
4. **Implementation** → Begin only after task and spec confirmation.

## Initialization

If this is the beginning of a session execute following prompts:

[init-project](./prompts/init-project.prompt.md)
[init-specs](./prompts/init-specs.prompt.md)
[init-tasks](./prompts/init-tasks.prompt.md)

## Commands

Try to match the user's input to one of the following commands, if you found a match execute the corresponding prompt, else ask the user to make themselves more clear

### Command Registry

...

## Additional Guidelines

- **Suggest Improvements Proactively:**
  - If you recognize opportunities for simplification, optimization, or alternative solutions beyond given specifications, explicitly suggest them before implementation.

- **Rule Simplicity:**
  - Avoid unnecessary complexity in rules. Focus clearly on outcomes and workflows rather than exhaustive detail on tooling or tech stacks.

