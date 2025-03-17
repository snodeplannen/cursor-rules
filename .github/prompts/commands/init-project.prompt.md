# Command Prompt for Coding Agent: Project Validation and Initialization

## Objective

Ensure the current workspace is a valid project. Support projects created with UV, projects with `.venv` and `requirements.txt`, and projects with Conda.

## Steps

1. **Check for Valid Project:**
    - Verify if the project is managed with UV by checking for UV configuration files.
    - Check for the presence of a `.venv` directory and a `requirements.txt` file.
    - Check for the presence of a `conda` environment configuration file (e.g., `environment.yml`).

2. **Prompt for Initialization:**
    - If the workspace is not a valid project, ask the user if they want to initialize the project.
    - Provide options for initialization:
      - UV: `uv init --package` followed by `uv sync`
      - Virtual Environment: Create `.venv` and `requirements.txt`
      - Conda: Create conda environment and `environment.yml`

## Example Prompt

```markdown
The current workspace is not a valid project. Would you like to initialize the project? Please choose one of the following options:

1. **UV Project**: Initialize with `uv init --package` followed by `uv sync`
2. **Virtual Environment**: Create `.venv` and `requirements.txt`
3. **Conda Environment**: Create `environment.yml`

Please enter the number corresponding to your choice:
```