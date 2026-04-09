FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    g++ \
    cmake \
    make \
    curl \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create workspace and logs directories
RUN mkdir -p /workspace/ClickHouse /logs/verifier

# Clone ClickHouse at the base commit (shallow clone for speed)
# Base commit: 61a4296fdce9d13cafb931cf73e4490b6d2bb315
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout --depth=200 https://github.com/ClickHouse/ClickHouse.git \
    && cd ClickHouse \
    && git fetch --depth=200 origin 61a4296fdce9d13cafb931cf73e4490b6d2bb315 \
    && git checkout 61a4296fdce9d13cafb931cf73e4490b6d2bb315

# No need to build ClickHouse - we'll test the logic directly via C++ test harness
# The test_outputs.py file compiles and tests the specific function logic

WORKDIR /workspace
