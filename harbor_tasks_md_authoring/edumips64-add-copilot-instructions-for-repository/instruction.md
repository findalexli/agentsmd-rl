# Add Copilot instructions for repository context and conventions

Source: [EduMIPS64/edumips64#1443](https://github.com/EduMIPS64/edumips64/pull/1443)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures GitHub Copilot coding agent with repository-specific context per best practices documentation.

Created `.github/copilot-instructions.md` covering:
- **Project architecture**: Java core (MIPS64 simulator), GWT web worker, React UI
- **Build system**: Gradle tasks and NPM scripts with key commands
- **Testing patterns**: End-to-end assembly tests, component unit tests, test initialization patterns
- **Code structure**: Package organization (`core/`, `ui/`, `client/`, `utils/`), test resources layout
- **Development workflow**: GitHub Flow with protected master, PR requirements
- **GWT specifics**: Web worker compilation caveats (war task wipes output directory)
- **Environment setup**: Dev container, Java 17+, Node 16+, Python 3.9+ requirements

This enables Copilot to understand project conventions, locate relevant code, and follow established patterns when making changes.

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-agent-tips).
> 
> <Onboard this repo></issue_description>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
> <comments>
> </comments>
> 


</details>

- Fixes EduMIPS64/edumips64

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
