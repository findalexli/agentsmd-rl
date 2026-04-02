FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/pytorch/pytorch.git /repo \
    && cd /repo \
    && git checkout 036b25f5a29dc58cbc62e7b976efb860ff128c3f

# Install minimal deps needed for testing (sympy for the codegen module)
RUN pip install --no-cache-dir sympy

# Configure git for the agent
RUN cd /repo && git config user.email "agent@test.com" && git config user.name "Agent"

ENV PYTHONPATH=/repo
RUN mkdir -p /logs/verifier

WORKDIR /repo