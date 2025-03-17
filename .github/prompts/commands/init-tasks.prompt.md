# Command Prompt for Coding Agent: Tasks Validation and Initialization

## Objective

Ensure the project has a properly structured task management system by checking for and initializing the `.project/tasks` directory and the `TASKS.md` index file.

## Steps

1. **Check for Valid Tasks Structure:**
    - Verify if the `.project/tasks` directory exists.
    - Check if the `TASKS.md` index file exists in the `.project` directory.

2. **Initialize if Missing:**
    - If either component is missing, create the necessary directory structure and files.
    - Create the `.project/tasks` directory if it doesn't exist.
    - Create the `TASKS.md` index file with proper formatting if it doesn't exist.

3. **Report Status:**
    - Inform the user about the current status of the tasks structure.
    - Provide confirmation that initialization was successful, if performed.

## Example Implementation

```markdown
## Tasks Structure Check

Checking for tasks directory and index file...

- `.project/tasks` directory: {STATUS}
- `.project/TASKS.md` index file: {STATUS}

{ACTION_TAKEN}

The task management system is now properly initialized. You can now:
- Create new tasks with `task create [name]`
- Update existing tasks with `task update [id] [status]`
- List all tasks with `task list`
```

## TASKS.md Template

If initialization is needed, create the TASKS.md file with the following template:

```markdown
# Project Tasks

This document serves as an index of all tasks for the project. Each task is linked below with its current status and metadata.

## Tasks List

| ID | Description | Spec Reference | State | Start Date | End Date |
|----|-------------|---------------|-------|------------|----------|
<!-- New tasks will be added here -->

## Task States

- **open**: Task is defined but work has not begun
- **in_progress**: Task is currently being implemented
- **closed**: Task has been completed and meets all acceptance criteria

## How to Use This Document

- Each task has a unique ID (TASK-YYYY-MM-DD-NN format) and is stored in the `.project/tasks/` directory
- Tasks define specific implementation work to fulfill project specifications
- Use the commands `task create`, `task update`, and `task list` to manage tasks
```
