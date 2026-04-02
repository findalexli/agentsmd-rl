FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git clone https://github.com/inclusionAI/AReaL.git /repo \
    && cd /repo \
    && git checkout 6860e70c08eae3014e12d9adf5411d648f7fceac \
    && git config user.email "agent@test" \
    && git config user.name "Agent"

# Install only minimal deps needed for testing
RUN pip install --no-cache-dir omegaconf pyyaml uvloop

RUN mkdir -p /logs/verifier

WORKDIR /repo