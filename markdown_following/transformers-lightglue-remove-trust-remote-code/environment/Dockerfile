FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none --no-checkout \
        https://github.com/huggingface/transformers.git /workspace/transformers

WORKDIR /workspace/transformers
RUN git sparse-checkout init --no-cone \
    && git sparse-checkout set \
        "utils/mlinter/*" \
        "src/transformers/models/lightglue/*" \
        "AGENTS.md" "CLAUDE.md" \
        ".ai/AGENTS.md" ".github/copilot-instructions.md" \
    && git checkout 09a0bbb21ac50eae76bec1c600ff711f135a4f91

RUN mkdir -p /logs/verifier

WORKDIR /workspace
