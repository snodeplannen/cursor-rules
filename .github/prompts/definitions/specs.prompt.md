# Specification definition prompt

Specifications in this project are managed systematically to ensure clarity, completeness, and traceability. Each specification is saved in the `.project/specs` directory, and an index of all specifications is maintained in `.project/SPECS.md` for a quick overview of project requirements.

## Specification Format

Each specification should follow the format below:

- **Unique Specification ID:** SPEC-YYYY-MM-DD-NN
- **Title:** A clear and concise title for the specification.
- **Description:** A detailed description of the feature, component, or requirement being specified.
- **Requirements:** Numbered and atomic requirements listed as checkable items:
  ```
  - [ ] Requirement 1: Clear, specific, testable requirement
  - [ ] Requirement 2: Another clear requirement
  ```
- **Acceptance Criteria:** Clear criteria that must be met for the specification to be considered implemented.
- **Metadata:**
    - **ID:** Unique identifier for the specification.
    - **Creation Date:** The date when the specification was created.
    - **Last Updated:** The date when the specification was last modified.
    - **Status:** Current status (e.g., draft, approved, implemented, deprecated).
    - **Completion Percentage:** Percentage of requirements completed.
- **Domain/Component:** The domain or component this specification belongs to.
- **Related Specifications:** Links to related specifications, if applicable.
- **Notes:** Additional context, constraints, or considerations.

## Specification Quality Guidelines

To ensure high-quality specifications:

1. **Avoid vague terms:** Replace words like "should," "would," "could," etc., with specific, testable language.
2. **Use atomic requirements:** Each requirement should describe exactly one thing.
3. **Include all required sections:** All specifications must have a description, requirements, and acceptance criteria.
4. **Ensure testability:** Requirements should be written so that their implementation can be verified.
5. **Organize by domain:** Specifications should be organized by domain or component.

## Specification Validation

Specifications will be regularly validated for:

- Quality issues (vague terms, non-atomic requirements)
- Implementation status (whether requirements have been implemented in code)
- Test coverage (whether requirements have corresponding tests)

By adhering to this format and these guidelines, we ensure that all specifications are well-documented, traceable, and drive high-quality implementation throughout the project lifecycle.