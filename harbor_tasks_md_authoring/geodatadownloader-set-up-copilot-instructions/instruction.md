# ✨ Set up Copilot instructions

Source: [mchaynes/geodatadownloader#108](https://github.com/mchaynes/geodatadownloader/pull/108)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Overview

This PR configures GitHub Copilot instructions for the geodatadownloader repository by adding a comprehensive `.github/copilot-instructions.md` file. This follows the best practices documented at [gh.io/copilot-coding-agent-tips](https://gh.io/copilot-coding-agent-tips) to help Copilot provide more contextually relevant and accurate code suggestions.

## What's Included

The Copilot instructions file provides detailed guidance on:

### Project Context
- **Overview**: Describes geodatadownloader as a client-side browser application for downloading ArcGIS feature layer data
- **Key Features**: Custom extents, column selection, and support for multiple export formats (GeoJSON, CSV, SHP, GPKG, PMTiles)
- **Architecture**: Client-side processing with no backend, using GDAL WebAssembly for data conversion

### Technical Stack
- React 18 with TypeScript and Vite
- ArcGIS API for JavaScript for map rendering
- GDAL3.js for format conversion
- Supabase for authentication and database
- Jest and Cypress for testing

### Development Guidelines
- **Code Style**: TypeScript configuration (`noImplicitAny: false`, strict null checks), ESLint rules (unused vars with `_` prefix)
- **Testing**: Location of test files (`app/__tests__/`), React Testing Library patterns, mocking strategies
- **Commands**: Installation, build, lint, and test commands with special considerations for CI environments

### Common Tasks
- Step-by-step instructions for adding new export formats (database-fi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
