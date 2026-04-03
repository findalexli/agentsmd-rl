FROM golang:1.26-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/vitessio/vitess.git /workspace/vitess && \
    cd /workspace/vitess && \
    git checkout 9a3646f7f16d38cec2efabc13cef5da800a72280 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vitess

# Pre-build sqlparser package to cache Go dependencies
RUN go build ./go/vt/sqlparser/... 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
