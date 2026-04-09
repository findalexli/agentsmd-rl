FROM openjdk:17-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG REPO=https://github.com/JetBrains/kotlin.git
ARG BASE_COMMIT=a304b4b5c79aa22c62ab5410caccaeb3a05c276a

RUN git clone --filter=blob:none --no-checkout $REPO /workspace/kotlin && \
    cd /workspace/kotlin && \
    git fetch --depth=1 origin $BASE_COMMIT && \
    git checkout $BASE_COMMIT

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Install pytest
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace/kotlin
