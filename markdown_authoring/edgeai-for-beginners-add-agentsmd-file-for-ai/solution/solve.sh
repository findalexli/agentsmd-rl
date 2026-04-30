#!/usr/bin/env bash
set -euo pipefail

cd /workspace/edgeai-for-beginners

# Idempotency guard
if grep -qF "EdgeAI for Beginners is a comprehensive educational repository teaching Edge AI " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,440 @@
+# AGENTS.md
+
+## Project Overview
+
+EdgeAI for Beginners is a comprehensive educational repository teaching Edge AI development with Small Language Models (SLMs). The course covers EdgeAI fundamentals, model deployment, optimization techniques, and production-ready implementations using Microsoft Foundry Local and various AI frameworks.
+
+**Key Technologies:**
+- Python 3.8+ (primary language for AI/ML samples)
+- .NET C# (AI/ML Samples)
+- JavaScript/Node.js with Electron (for desktop applications)
+- Microsoft Foundry Local SDK
+- Microsoft Windows ML 
+- VSCode AI Toolkit
+- OpenAI SDK
+- AI Frameworks: LangChain, Semantic Kernel, Chainlit
+- Model Optimization: Llama.cpp, Microsoft Olive, OpenVINO, Apple MLX
+
+**Repository Type:** Educational content repository with 8 modules and 10 comprehensive sample applications
+
+**Architecture:** Multi-module learning path with practical samples demonstrating edge AI deployment patterns
+
+## Repository Structure
+
+```
+edgeai-for-beginners/
+├── introduction.md          # Course introduction and overview
+├── Module01-07/            # Core educational modules (Markdown)
+├── Module08/               # Foundry Local toolkit with 10 samples
+│   ├── samples/01-06/     # Foundation samples (Python)
+│   ├── samples/07/        # API client (Python)
+│   ├── samples/08/        # Windows 11 chat app (Electron)
+│   └── samples/09-10/     # Advanced multi-agent systems (Python)
+├── translations/          # Multi-language translations (50+ languages)
+├── translated_images/     # Localized images
+└── imgs/                  # Course images and assets
+```
+
+## Setup Commands
+
+### Repository Setup
+
+```bash
+# Clone the repository
+git clone https://github.com/microsoft/edgeai-for-beginners.git
+cd edgeai-for-beginners
+
+# No build step required - this is primarily an educational content repository
+```
+
+### Python Sample Setup (Module08 and Python samples)
+
+```bash
+# Create and activate virtual environment
+python -m venv .venv
+# On Windows
+.venv\Scripts\activate
+# On macOS/Linux
+source .venv/bin/activate
+
+# Install dependencies for Module08 samples
+cd Module08
+pip install -r requirements.txt
+```
+
+### Node.js Sample Setup (Sample 08 - Windows Chat App)
+
+```bash
+cd Module08/samples/08
+npm install
+
+# Start in development mode
+npm run dev
+
+# Build for production
+npm run build
+
+# Create installer
+npm run dist
+```
+
+### Foundry Local Setup
+
+Foundry Local is required to run the Module08 samples:
+
+```bash
+# Start Foundry Local service with a model
+foundry model run phi-4-mini
+
+# Verify service is running
+curl http://localhost:8000/health
+```
+
+## Development Workflow
+
+### Content Development
+
+This repository contains primarily **Markdown educational content**. When making changes:
+
+1. Edit `.md` files in the appropriate module directories
+2. Follow existing formatting patterns
+3. Ensure code examples are accurate and tested
+4. Update corresponding translated content if necessary (or let automation handle it)
+
+### Sample Application Development
+
+For Python samples (samples 01-07, 09-10):
+```bash
+cd Module08
+python samples/01/chat_quickstart.py "Test message"
+```
+
+For Electron sample (sample 08):
+```bash
+cd Module08/samples/08
+npm run dev  # Development with hot reload
+```
+
+### Testing Sample Applications
+
+Python samples don't have automated tests but can be validated by running them:
+```bash
+# Test basic chat functionality
+python samples/01/chat_quickstart.py "Hello"
+
+# Test with specific model
+set MODEL=phi-4-mini
+python samples/02/openai_sdk_client.py
+```
+
+Electron sample has test infrastructure:
+```bash
+cd Module08/samples/08
+npm test           # Run unit tests
+npm run test:e2e   # Run end-to-end tests
+npm run lint       # Check code style
+```
+
+## Testing Instructions
+
+### Content Validation
+
+The repository uses automated translation workflows. No manual testing required for translations.
+
+**Manual validation for content changes:**
+1. Review Markdown rendering by previewing `.md` files
+2. Verify all links point to valid targets
+3. Test any code snippets included in documentation
+4. Check that images load correctly
+
+### Sample Application Testing
+
+**Module08/samples/08 (Electron app) has comprehensive testing:**
+```bash
+cd Module08/samples/08
+
+# Run all tests
+npm test
+
+# Run unit tests only
+npm test -- --testPathPattern=unit
+
+# Run integration tests
+npm run test:integration
+
+# Run E2E tests
+npm run test:e2e
+
+# Check test coverage
+npm test -- --coverage
+```
+
+**Python samples should be manually tested:**
+```bash
+# Each sample can be run directly
+python samples/01/chat_quickstart.py "Test prompt"
+python samples/04/chainlit_rag.py
+python samples/09/multi_agent_system.py
+```
+
+## Code Style Guidelines
+
+### Markdown Content
+
+- Use consistent heading hierarchy (# for title, ## for main sections, ### for subsections)
+- Include code blocks with language specifiers: ```python, ```bash, ```javascript
+- Follow existing formatting for tables, lists, and emphasis
+- Keep lines readable (aim for ~80-100 characters, but not strict)
+- Use relative links for internal references
+
+### Python Code Style
+
+- Follow PEP 8 conventions
+- Use type hints where appropriate
+- Include docstrings for functions and classes
+- Use meaningful variable names
+- Keep functions focused and concise
+
+### JavaScript/Node.js Code Style
+
+```bash
+# Electron sample follows ESLint configuration
+cd Module08/samples/08
+npm run lint        # Check for style issues
+npm run lint:fix    # Auto-fix style issues
+npm run format      # Format with Prettier
+```
+
+**Key conventions:**
+- ESLint configuration provided in sample 08
+- Prettier for code formatting
+- Use modern ES6+ syntax
+- Follow existing patterns in the codebase
+
+## Pull Request Guidelines
+
+### Title Format
+```
+[ModuleXX] Brief description of change
+```
+or
+```
+[Module08/samples/XX] Description for sample changes
+```
+
+### Before Submitting
+
+**For content changes:**
+- Preview all modified Markdown files
+- Verify links and images work
+- Check for typos and grammatical errors
+
+**For sample code changes (Module08/samples/08):**
+```bash
+npm run lint
+npm test
+```
+
+**For Python sample changes:**
+- Test the sample runs successfully
+- Verify error handling works
+- Check compatibility with Foundry Local
+
+### Review Process
+
+- Educational content changes are reviewed for accuracy and clarity
+- Code samples are tested for functionality
+- Translation updates are handled automatically by GitHub Actions
+
+## Translation System
+
+**IMPORTANT:** This repository uses automated translation via GitHub Actions.
+
+- Translations are in `/translations/` directory (50+ languages)
+- Automated via `co-op-translator.yml` workflow
+- **DO NOT manually edit translation files** - they will be overwritten
+- Edit only English source files in root and module directories
+- Translations are automatically generated on push to `main` branch
+
+## Foundry Local Integration
+
+Most Module08 samples require Microsoft Foundry Local to be running:
+
+### Starting Foundry Local
+```bash
+# Start Foundry Local 
+foundry service start
+
+#foundry service host and port are displayed after running this command or `foundry service status`
+
+# Run a specific model
+foundry model run phi-4-mini
+
+# Or run with different models
+foundry model run qwen2.5-coder-0.5b
+foundry model run mistral-7b
+```
+
+### Verifying Foundry Local
+```bash
+# Check service health
+curl http://127.0.0.1:55769/
+
+# the Port and PID will be displayed when running `foundry service start`
+
+# List loaded models
+curl http://localhost:55769/v1/models
+```
+
+### Environment Variables for Samples
+
+Most samples use these environment variables:
+```bash
+# Foundry Local configuration (defaults work for most cases)
+set BASE_URL=http://localhost:55769
+set MODEL=phi-4-mini
+set API_KEY=
+
+# For Azure OpenAI fallback (optional)
+set AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
+set AZURE_OPENAI_API_KEY=your-api-key
+set AZURE_OPENAI_API_VERSION=2024-08-01-preview
+```
+
+## Build and Deployment
+
+### Content Deployment
+
+This repository is primarily documentation - no build process required for content.
+
+### Sample Application Building
+
+**Electron Application (Module08/samples/08):**
+```bash
+cd Module08/samples/08
+
+# Development build
+npm run dev
+
+# Production build
+npm run build
+
+# Create Windows installer
+npm run dist
+
+# Create portable executable
+npm run pack
+```
+
+**Python Samples:**
+No build process - samples are run directly with Python interpreter.
+
+## Common Issues and Troubleshooting
+
+### Foundry Local Not Running
+**Issue:** Samples fail with connection errors
+
+**Solution:**
+```bash
+# Start Foundry Local service
+foundry model run phi-4-mini
+
+# Verify it's running
+curl http://localhost:55769/health
+```
+
+### Python Virtual Environment Issues
+**Issue:** Module import errors
+
+**Solution:**
+```bash
+# Ensure virtual environment is activated
+# Windows
+.venv\Scripts\activate
+# macOS/Linux
+source .venv/bin/activate
+
+# Reinstall dependencies
+pip install -r requirements.txt
+```
+
+### Electron Build Issues
+**Issue:** npm install or build failures
+
+**Solution:**
+```bash
+cd Module08/samples/08
+# Clean install
+npm run clean
+rm -rf node_modules package-lock.json
+npm install
+```
+
+### Translation Workflow Conflicts
+**Issue:** Translation PR conflicts with your changes
+
+**Solution:**
+- Only edit English source files
+- Let the automated translation workflow handle translations
+- If conflicts occur, merge `main` into your branch after translations are merged
+
+## Additional Resources
+
+### Learning Paths
+- **Beginner Path:** Modules 01-02 (7-9 hours)
+- **Intermediate Path:** Modules 03-04 (9-11 hours)
+- **Advanced Path:** Modules 05-07 (12-15 hours)
+- **Expert Path:** Module 08 (8-10 hours)
+
+### Key Module Content
+- **Module01:** EdgeAI fundamentals and real-world case studies
+- **Module02:** Small Language Model (SLM) families and architectures
+- **Module03:** Local and cloud deployment strategies
+- **Module04:** Model optimization with multiple frameworks
+- **Module05:** SLMOps - production operations
+- **Module06:** AI agents and function calling
+- **Module07:** Platform-specific implementations
+- **Module08:** Foundry Local toolkit with 10 comprehensive samples
+
+### External Dependencies
+- [Microsoft Foundry Local](https://foundry.microsoft.com/) - Local AI model runtime
+- [Llama.cpp](https://github.com/ggml-org/llama.cpp) - Optimization framework
+- [Microsoft Olive](https://microsoft.github.io/Olive/) - Model optimization toolkit
+- [OpenVINO](https://docs.openvino.ai/) - Intel's optimization toolkit
+
+## Project-Specific Notes
+
+### Module08 Sample Applications
+
+The repository includes 10 comprehensive sample applications:
+
+1. **01-REST Chat Quickstart** - Basic OpenAI SDK integration
+2. **02-OpenAI SDK Integration** - Advanced SDK features
+3. **03-Model Discovery & Benchmarking** - Model comparison tools
+4. **04-Chainlit RAG Application** - Retrieval-augmented generation
+5. **05-Multi-Agent Orchestration** - Basic agent coordination
+6. **06-Models-as-Tools Router** - Intelligent model routing
+7. **07-Direct API Client** - Low-level API integration
+8. **08-Windows 11 Chat App** - Native Electron desktop application
+9. **09-Advanced Multi-Agent System** - Complex agent orchestration
+10. **10-Foundry Tools Framework** - LangChain/Semantic Kernel integration
+
+Each sample demonstrates different aspects of edge AI development with Foundry Local.
+
+### Performance Considerations
+
+- SLMs are optimized for edge deployment (2-16GB RAM)
+- Local inference provides 50-500ms response times
+- Quantization techniques achieve 75% size reduction with 85% performance retention
+- Real-time conversation capabilities with local models
+
+### Security and Privacy
+
+- All processing happens locally - no data sent to cloud
+- Suitable for privacy-sensitive applications (healthcare, finance)
+- Meets data sovereignty requirements
+- Foundry Local runs entirely on local hardware
+
+---
+
+**This is an educational repository focused on teaching Edge AI development. The primary contribution pattern is improving educational content and adding/enhancing sample applications that demonstrate Edge AI concepts.**
PATCH

echo "Gold patch applied."
