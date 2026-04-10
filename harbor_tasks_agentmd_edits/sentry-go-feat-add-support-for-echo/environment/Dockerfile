FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pytest for testing
RUN pip3 install pytest --break-system-packages

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/getsentry/sentry-go.git /workspace/sentry-go && \
    cd /workspace/sentry-go && \
    git checkout 6ba06389e351fc94be995c2c59382575c88f1b82 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sentry-go

# Pre-download echo/v4 deps so base state builds
RUN cd echo && go mod download

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
