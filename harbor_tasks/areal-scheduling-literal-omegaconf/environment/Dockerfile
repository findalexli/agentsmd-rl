FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin 6860e70c08eae3014e12d9adf5411d648f7fceac && \
    git checkout FETCH_HEAD

# Install only minimal deps needed for testing
RUN pip install --no-cache-dir omegaconf pyyaml uvloop

RUN mkdir -p /logs/verifier

WORKDIR /repo