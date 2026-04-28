"""Behavioral checks for azure-openai-rag-workshop-docs-add-agentsmd-closes-45 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/azure-openai-rag-workshop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/create-agents.md.prompt.md')
    assert '- For example, look for files that may contain the project name, idea, vision, requirements, technology stack and constraints. This may include README files, project documentation, configuration files' in text, "expected to find: " + '- For example, look for files that may contain the project name, idea, vision, requirements, technology stack and constraints. This may include README files, project documentation, configuration files'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/create-agents.md.prompt.md')
    assert '- **Input**: Any files that may provide context about the project, including but not limited to README files, documentation, configuration files (e.g., package.json, pyproject.toml, etc.), CI/CD workf' in text, "expected to find: " + '- **Input**: Any files that may provide context about the project, including but not limited to README files, documentation, configuration files (e.g., package.json, pyproject.toml, etc.), CI/CD workf'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/create-agents.md.prompt.md')
    assert 'When creating the `AGENTS.md` file, prioritize clarity, completeness, and actionability. The goal is to give any coding agent enough context to effectively contribute to the project without requiring ' in text, "expected to find: " + 'When creating the `AGENTS.md` file, prioritize clarity, completeness, and actionability. The goal is to give any coding agent enough context to effectively contribute to the project without requiring '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'A monorepo sample + workshop showing how to build a Retrieval‑Augmented Generation (RAG) chat experience using LangChain.js with Azure OpenAI (optionally Qdrant) and expose it through a Fastify backen' in text, "expected to find: " + 'A monorepo sample + workshop showing how to build a Retrieval‑Augmented Generation (RAG) chat experience using LangChain.js with Azure OpenAI (optionally Qdrant) and expose it through a Fastify backen'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Subscription-scope deployment creates resource group, container apps env, registry, static web app, optional search service, optional Qdrant, OpenAI resource (unless `openAiUrl` provided), identitie' in text, "expected to find: " + '- Subscription-scope deployment creates resource group, container apps env, registry, static web app, optional search service, optional Qdrant, OpenAI resource (unless `openAiUrl` provided), identitie'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Vector store abstraction: Both Azure AI Search and Qdrant dependencies included — ensure conditional logic in code respects `useQdrant` flag (code agents should not assume only one path).' in text, "expected to find: " + '- Vector store abstraction: Both Azure AI Search and Qdrant dependencies included — ensure conditional logic in code respects `useQdrant` flag (code agents should not assume only one path).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('src/backend/AGENTS.md')
    assert '- Responsibilities: Accept chat requests, perform embedding + vector similarity, construct prompts with retrieved context, call Azure OpenAI (or provided OpenAI endpoint).' in text, "expected to find: " + '- Responsibilities: Accept chat requests, perform embedding + vector similarity, construct prompts with retrieved context, call Azure OpenAI (or provided OpenAI endpoint).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('src/backend/AGENTS.md')
    assert '- Keep Fastify plugins modular (autoload pattern is present). Add new routes/plugins under standard directories (match existing layout when extending).' in text, "expected to find: " + '- Keep Fastify plugins modular (autoload pattern is present). Add new routes/plugins under standard directories (match existing layout when extending).'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('src/backend/AGENTS.md')
    assert '- Minimize unnecessary embedding calls (reuse embeddings where possible if caching layer is introduced—none exists yet; do not add without request).' in text, "expected to find: " + '- Minimize unnecessary embedding calls (reuse embeddings where possible if caching layer is introduced—none exists yet; do not add without request).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('src/frontend/AGENTS.md')
    assert '- Wrong API URL: Confirm build hook in root `azure.yaml` sets `BACKEND_API_URI` before `npm run build` for deployment.' in text, "expected to find: " + '- Wrong API URL: Confirm build hook in root `azure.yaml` sets `BACKEND_API_URI` before `npm run build` for deployment.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('src/frontend/AGENTS.md')
    assert '- Runtime backend base URL injected at build through env var `BACKEND_API_URI` -> `VITE_BACKEND_API_URI`.' in text, "expected to find: " + '- Runtime backend base URL injected at build through env var `BACKEND_API_URI` -> `VITE_BACKEND_API_URI`.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('src/frontend/AGENTS.md')
    assert '- Vite config manually chunks vendor modules. When adding new large deps, confirm chunking still optimal.' in text, "expected to find: " + '- Vite config manually chunks vendor modules. When adding new large deps, confirm chunking still optimal.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('src/ingestion/AGENTS.md')
    assert '- Keep parsing & chunking modular (add new file format handlers as separate utilities rather than modifying core handler heavily).' in text, "expected to find: " + '- Keep parsing & chunking modular (add new file format handlers as separate utilities rather than modifying core handler heavily).'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('src/ingestion/AGENTS.md')
    assert '- Responsibilities: Accept PDF files, parse (pdf-parse), produce embeddings via Azure OpenAI, upsert vectors into selected store.' in text, "expected to find: " + '- Responsibilities: Accept PDF files, parse (pdf-parse), produce embeddings via Azure OpenAI, upsert vectors into selected store.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('src/ingestion/AGENTS.md')
    assert '- LangChain / Vector: `@langchain/community`, `@langchain/qdrant`, `@azure/search-documents`, `@azure/identity`.' in text, "expected to find: " + '- LangChain / Vector: `@langchain/community`, `@langchain/qdrant`, `@azure/search-documents`, `@azure/identity`.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('trainer/AGENTS.md')
    assert '- Low default capacity to avoid quota deployment failures; adjust after deployment for > minimal class sizes (e.g., 200 TPM for ~50 attendees suggested in README).' in text, "expected to find: " + '- Low default capacity to avoid quota deployment failures; adjust after deployment for > minimal class sizes (e.g., 200 TPM for ~50 attendees suggested in README).'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('trainer/AGENTS.md')
    assert '- Proxy service exposes Azure OpenAI-compatible endpoints; attendees point their environment to proxy URL before provisioning (`AZURE_OPENAI_URL`).' in text, "expected to find: " + '- Proxy service exposes Azure OpenAI-compatible endpoints; attendees point their environment to proxy URL before provisioning (`AZURE_OPENAI_URL`).'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('trainer/AGENTS.md')
    assert '- Slides + workshop content referenced (hosted externally) but source for slides/workshop lives under `docs/` at repo root.' in text, "expected to find: " + '- Slides + workshop content referenced (hosted externally) but source for slides/workshop lives under `docs/` at repo root.'[:80]

