FROM eclipse-temurin:11-jdk-jammy

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip tmux build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use blob filter)
RUN git clone --filter=blob:none https://github.com/apache/beam.git /workspace/beam && \
    cd /workspace/beam && \
    git checkout 28a0cb14ebd018e3550637ded153569d49e66f66 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
