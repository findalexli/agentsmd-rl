FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update -qq && apt-get install -y -qq \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone vllm at the pre-fix commit
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin b2bc736b1247a76e6ab1cfbe38ae39c3c307de40 && \
    git checkout FETCH_HEAD

# No heavy deps needed — we're testing a Dockerfile text change
RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for agent commits
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

ENV PYTHONPATH=/repo