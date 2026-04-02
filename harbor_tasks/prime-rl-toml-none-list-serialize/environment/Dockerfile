FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (before fix)
RUN git clone https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout a25b3e7a18e76999558a888c1ab1f8e5cd0e3831

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir pydantic pydantic-settings

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl

# Install minimal deps needed for testing (just pydantic + pydantic_config + tomli_w)
RUN pip install --no-cache-dir pydantic tomli_w pyyaml pytest pytest-json-ctrf
RUN pip install --no-cache-dir "pydantic-config @ git+https://github.com/samsja/pydantic_config.git@main"

ENV PYTHONPATH="/workspace/prime-rl/src:${PYTHONPATH:-}"