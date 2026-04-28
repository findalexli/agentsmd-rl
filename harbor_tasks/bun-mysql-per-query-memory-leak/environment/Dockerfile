FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pytest python3-yaml python3-pip python3-venv xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 9a27ef75697d713dba18b7a9762308197014ecca && \
    git checkout FETCH_HEAD && \
    git config user.name "test" && \
    git config user.email "test@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /repo
RUN pip3 install --break-system-packages pytest pytest-json-ctrf

# Install zig for behavioral compilation tests (zig ast-check)
# Pinned to 0.14.0 for reproducibility
RUN curl -fsSL https://ziglang.org/download/0.14.0/zig-linux-x86_64-0.14.0.tar.xz -o /tmp/zig.tar.xz && \
    tar -xJf /tmp/zig.tar.xz -C /tmp && \
    cp /tmp/zig-linux-x86_64-0.14.0/zig /usr/local/bin/zig && \
    rm -rf /tmp/zig.tar.xz /tmp/zig-linux-x86_64-0.14.0
