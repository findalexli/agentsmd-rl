FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /repo && \
    cd /repo && \
    git checkout c13daab68aa40cb58f2c643a650b5db48e986935

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git user for patches
RUN git config user.email "test@test.com" && \
    git config user.name "Test"

# Install minimal deps needed for testing (just gradio core, no heavy extras)
RUN pip install --no-cache-dir -e "." 2>/dev/null || \
    pip install --no-cache-dir typing_extensions

ENV PYTHONPATH=/repo