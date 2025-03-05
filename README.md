# Cursor Rules Collection

> ⚠️ **Important**: If you're using Cursor without rules, you're doing it wrong!

This repository contains a collection of custom rules for the [Cursor](https://cursor.sh/) AI coding assistant that significantly enhance its capabilities. These rules provide structure, automation, and consistency to your AI-assisted coding workflow.

## What are Cursor Rules?

Cursor rules (in .mdc format) are instructions that guide how the AI assistant behaves, processes information, and generates code. They act as a "stdlib" or framework for the AI, ensuring that it follows best practices, coding standards, and project-specific requirements.

Rules allow you to:
- Automate repetitive tasks
- Enforce coding standards
- Implement workflows that boost productivity
- Create specifications that drive implementation
- Maintain consistency across your codebase

## Rules in this Repository

### Git Commit Rule
`git-commit-rule.mdc`: Automatically commits changes made by CursorAI using conventional commits format.
- Detects file changes, build successes, and successful unit tests
- Only commits code when builds and/or unit tests pass (for languages without formal build processes, unit tests are the validation mechanism)
- If tests fail, Cursor will attempt to fix issues until all tests pass
- Categorizes changes appropriately (feat, fix, docs, etc.)
- Creates properly formatted commit messages
- Special handling for specification files

### Request Specs Rule
`request-specs-rule.mdc`: Implements requirements engineering with automatic spec file creation.
- Categorizes user requests by domain
- Writes specifications to `.cursor/specs/` folder
- Creates a master SPECS.md document linking to all specs
- Enforces "spec first" development (no implementation without specs)

### Development Workflow Rule
`development-rule.mdc`: Controls the development workflow with comprehensive task tracking.
- Creates task files in `.cursor/tasks/` with unique IDs and structured metadata
- Maintains a central TASKS.md index of all tasks with their status
- Tracks each task's:
  - Description and header
  - Relevant specifications
  - Acceptance criteria (always including unit tests)
  - Start and end dates
  - State (📝 Open, 🔄 Active, ✅ Done)
  - Learnings and insights gained during implementation
- Supports multiple concurrent tasks and planning sessions
- Ensures all acceptance criteria (including tests) pass before task completion
- Preserves learnings in `.cursor/learnings/` for future reference

### Information Tracking Rule
`information-tracking-rule.mdc`: Manages knowledge tracking and documentation organization.
- Captures and organizes two types of knowledge:
  - **Learnings**: Knowledge gained during development or user interaction
  - **Documents**: Information shared by users for reference
- Creates structured learning files in `.cursor/learnings/` with:
  - Unique ID and title
  - Short and detailed descriptions
  - Links to relevant code, tasks, specs, and documents
  - Timestamps for reference
- Automatically processes user-provided documents in `.cursor/docs/`
- Maintains centralized indexes:
  - LEARNINGS.md: Catalog of all captured knowledge
  - DOCUMENTS.md: Registry of user-provided documentation
- Creates cross-references between related information assets
- Automatically generates learnings when new documents are added
- Ensures knowledge is preserved and discoverable throughout the project

## Inspiration

This approach was inspired by [Geoffrey Huntley's method](https://ghuntley.com/specs/) of using Cursor AI effectively. Huntley demonstrates how combining specifications with technical rules creates a powerful workflow that can dramatically increase development productivity.

As Huntley explains:
> "When you use '/specs' method with the 'stdlib' method in conjunction with a programming language that provides compiler soundness (driven by good types) and compiler errors, the results are incredible. You can drive hands-free output of N factor (entire weeks' worth) of co-workers in hours."

## Getting Started

1. Clone this repository or download the rules
2. Place the .mdc files in your project's `.cursor/rules/` directory
3. Start Cursor and begin interacting with the AI
4. The rules will automatically take effect during your conversations

### Practical Workflow

Follow this concrete workflow to get the most out of these rules:

1. **Initial Requirements Discussion**
   - Open Cursor and describe your project/feature requirements to the AI
   - The AI will automatically create specification files in `.cursor/specs/` based on your discussion
   - A central `SPECS.md` file will be generated or updated with links to all domain-specific specs

2. **Review & Refine Specifications**
   - Review the generated specs files to ensure they accurately capture requirements
   - Continue the conversation with AI to refine specs as needed
   - Each refinement will update the relevant specification files

3. **Development Based on Specifications**
   - Ask the AI to implement features based on the specifications: "Please implement the feature described in specs/auth/login.md"
   - The AI will reference the specs during implementation
   - If a feature request doesn't have corresponding specs, the AI will first create them before implementation

4. **Automatic Commits**
   - As the AI makes changes to files, the git-commit-rule automatically stages and commits them
   - Commits follow conventional commit format (feat, fix, docs, etc.) based on the nature of the change
   - Commit messages are automatically generated with appropriate type, scope, and description

5. **Continuous Development Loop**
   - For new features: start new conversation → generate specs → implement → automatic commits
   - For refinements: discuss changes → update specs → implement changes → automatic commits

This workflow ensures all development is specification-driven and automatically documented through well-structured Git commits.

## Something Missing?

One of the most powerful aspects of Cursor is its ability to extend itself! You can ask Cursor to create new rules that address your specific workflow needs:

### How to Ask Cursor to Implement New Rules

1. **Identify a Workflow Pain Point**: Think about a repetitive task or pattern you'd like to automate

2. **Ask Cursor to Create a Rule**: Use prompts like:
   ```
   Create a Cursor IDE MDC rule that automatically [describes desired behavior].
   The rule should be saved to .cursor/rules/[rule-name].mdc
   ```

3. **Example Prompts**:
   - "Create a Cursor IDE MDC rule that automatically generates unit tests whenever I create a new function"
   - "Create a Cursor MDC rule for TypeScript files that enforces consistent error handling patterns"
   - "Create a rule that inserts license headers into new files based on file type"

4. **Refine the Rule**: Cursor will generate a rule file, but you can continue the conversation to refine it:
   ```
   That looks good, but can you modify the rule to also handle [additional case]?
   ```

5. **Test and Iterate**: Apply the rule in your workflow and ask Cursor to make adjustments as needed

This meta-capability - using Cursor to extend Cursor - demonstrates the true power of rule-based AI assistance. You're not limited to the rules in this repository; you can create a completely customized workflow tailored to your project's needs.

## Contributing

Feel free to contribute your own rules or improvements to existing ones via pull requests.

## License

MIT License

Copyright (c) 2023 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

Remember: The true power of AI coding assistants comes not from treating them as mere code completion tools, but from providing them with the proper structure, specifications, and technical guidance to deliver complete, high-quality implementations.
