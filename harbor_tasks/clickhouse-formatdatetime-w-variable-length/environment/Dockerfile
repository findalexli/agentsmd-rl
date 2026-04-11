# Dockerfile for ClickHouse formatDateTime benchmark
FROM ubuntu:24.04

# Prevent interactive prompts during apt
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install build essentials and dependencies
RUN apt-get update && apt-get install -y     build-essential     git     cmake     ccache     python3     python3-pip     ninja-build     nasm     yasm     gawk     lsb-release     wget     software-properties-common     gnupg     curl     file     && rm -rf /var/lib/apt/lists/*

# Install clang
RUN bash -c "$(wget -O - https://apt.llvm.org/llvm.sh)" ||     (apt-get install -y clang && update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100)

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Install pytest
RUN pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Copy the ClickHouse repo (will be provided at build time via build context)
WORKDIR /workspace
COPY ClickHouse ClickHouse

WORKDIR /workspace/ClickHouse

# Reinitialize git repository (required because COPY doesn't preserve git metadata properly)
RUN git init . && git config user.email "test@test.com" && git config user.name "Test"
