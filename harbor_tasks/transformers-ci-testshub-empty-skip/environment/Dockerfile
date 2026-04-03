FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global advice.detachedHead false

# Clone transformers at base commit (before the fix)
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin c9faacd7d57459157656bdffe049dabb6293f011 && \
    git checkout FETCH_HEAD

# No heavy deps needed — tests only exercise utils/tests_fetcher.py (pure Python, stdlib only)
# Just need pyyaml for judge
RUN pip install --no-cache-dir pyyaml gitpython pytest pytest-json-ctrf ruff

# Configure git for agent commits
RUN cd /workspace/transformers && git config user.name "agent" && git config user.email "agent@test"

ENV PYTHONPATH="/workspace/transformers/src"
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers