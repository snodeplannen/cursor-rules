# Cursor Rules Collection

> ⚠️ **Important**: If you're using Cursor without rules, you're using it incorrectly!

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
- Detects file changes and build successes
- Categorizes changes appropriately (feat, fix, docs, etc.)
- Creates properly formatted commit messages
- Special handling for specification files

### Request Specs Rule
`request-specs-rule.mdc`: Implements requirements engineering with automatic spec file creation.
- Categorizes user requests by domain
- Writes specifications to `.cursor/specs/` folder
- Creates a master SPECS.md document linking to all specs
- Enforces "spec first" development (no implementation without specs)

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

## Contributing

Feel free to contribute your own rules or improvements to existing ones via pull requests.

## License

[Specify your license here]

---

Remember: The true power of AI coding assistants comes not from treating them as mere code completion tools, but from providing them with the proper structure, specifications, and technical guidance to deliver complete, high-quality implementations.
