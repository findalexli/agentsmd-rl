FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

# Install transformers v5+ (which adds strict validation to PretrainedConfig)
# and huggingface_hub for the @strict decorator used by some configs
RUN pip install --no-cache-dir 'transformers>=5.0.0' 'huggingface_hub>=0.25.0' pytest pytest-json-ctrf

WORKDIR /workspace

# Clone vllm at the commit BEFORE the fix
RUN git clone https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git checkout 28048bd6b09cb164a934a8c134b7d7a7f4733b4f

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/vllm