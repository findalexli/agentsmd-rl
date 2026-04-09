# Bun shell sentinel hardening validation task
FROM oven/bun:1.2.8-slim

# Install python3 + pytest (needed by test runner)
RUN apt-get update -qq && apt-get install -y -qq python3 python3-pip git curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install --break-system-packages pytest pytest-json-ctrf || \
    pip3 install pytest pytest-json-ctrf

# Setup workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone bun repo at base commit (pre-fix)
ARG BASE_COMMIT=f06119ad0cd49bba93908329ef5e53a39c50fb70
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git && \
    cd bun && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Copy tests and solution
COPY tests/ /tests/
COPY solution/ /solution/

# Default command runs tests
CMD ["/tests/test.sh"]
