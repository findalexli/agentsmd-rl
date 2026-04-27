FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates patch \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4

WORKDIR /workspace

# Sparse partial-clone: only the directories an agent needs to write
# AGENTS.md for the Build Tools API area.
#   - .ai/                : repo-wide guidelines (the area-table convention)
#   - compiler/build-tools: the area itself (modules, source, tests, READMEs)
#   - compiler/AGENTS.md, compiler/psi/AGENTS.md
#   - libraries/tools/kotlin-gradle-plugin{-api}/AGENTS.md
#       reference AGENTS.md files (different shapes the agent can compare)
RUN mkdir /workspace/kotlin && cd /workspace/kotlin && \
    git init -q && \
    git config --global --add safe.directory /workspace/kotlin && \
    git remote add origin https://github.com/JetBrains/kotlin.git && \
    git sparse-checkout init --no-cone && \
    git sparse-checkout set \
        '/.ai/' \
        '/compiler/build-tools/' \
        '/compiler/AGENTS.md' \
        '/compiler/psi/AGENTS.md' \
        '/compiler/fir/analysis-tests/AGENTS.md' \
        '/libraries/tools/kotlin-gradle-plugin/AGENTS.md' \
        '/libraries/tools/kotlin-gradle-plugin-api/AGENTS.md' \
        '/analysis/AGENTS.md' && \
    git fetch --depth=1 --filter=blob:none origin 05427c4231216b07bd7607b77095ec011d21fbfa && \
    git checkout 05427c4231216b07bd7607b77095ec011d21fbfa

WORKDIR /workspace/kotlin

RUN mkdir -p /logs/verifier
