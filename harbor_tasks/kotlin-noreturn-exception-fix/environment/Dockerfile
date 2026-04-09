FROM python:3.12-slim

# Install dependencies: git, curl, and clang for C++ verification
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Clone the Kotlin repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=c962899eaa18746e5b6f2e4d9a6d0f5785d49a06
RUN git clone --filter=blob:none --depth=100 https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
