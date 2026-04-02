FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git clone https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 8bc75137b24ba8a8571b49b9b006741819c0518b && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install only tinycolor2 for testing (avoid full monorepo install)
RUN cd /workspace/gradio/js/colorpicker && \
    rm -f package.json package-lock.json && \
    echo '{"private":true}' > package.json && \
    npm install tinycolor2@1

ENV PYTHONPATH=/workspace/gradio
RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio