# Add comprehensive GitHub Copilot instructions for Endurain development workflow

Source: [endurain-project/endurain#322](https://github.com/endurain-project/endurain/pull/322)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds a comprehensive `.github/copilot-instructions.md` file that provides GitHub Copilot coding agents with detailed instructions on how to work effectively in the Endurain codebase.

## Key Features

**Validated Development Workflows:**
- Complete frontend development setup with Vue.js, Vite, and npm
- Docker-based full-stack development approach
- All commands tested and timing measured for accurate timeout recommendations

**Critical Timing and Timeout Information:**
- Frontend build: 9 seconds
- npm install: 5-21 seconds (depending on cache)
- npm format: 2-6 seconds
- Docker builds: 15+ minutes with explicit "NEVER CANCEL" warnings

**Manual Validation Scenarios:**
- Specific UI testing requirements for the login page
- Screenshot validation guidelines
- End-to-end workflow verification steps

**Known Limitations Documentation:**
- ESLint configuration issues (needs flat config migration)
- Docker SSL certificate problems in CI environments
- Backend Python 3.13 requirement vs system Python 3.12
- Current absence of unit tests

**Architecture Overview:**
- Vue.js 3 frontend with Vite build system
- Python FastAPI backend with SQLAlchemy
- PostgreSQL/MariaDB database support
- Strava and Garmin Connect integrations

## Validation

All documented commands have been thoroughly tested:

```bash
# Fresh install and build workflow
cd frontend/app
npm install          # ✅ 5-21 seconds
npm run build        # ✅ 9 seconds  
npm run format       # ✅ 2-6 seconds
npm run dev 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
