FROM mcr.microsoft.com/dotnet/sdk:8.0

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/maui && \
    cd /workspace/maui && \
    git remote add origin https://github.com/dotnet/maui.git && \
    git fetch --depth=1 origin ecd6428d324e395ca07f8d375600c0fc93d0dd3c && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Install python packages for test runner
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    pip3 install pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
