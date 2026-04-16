# Dockerfile for selenium-keys-charsequence-contract task
FROM eclipse-temurin:17-jdk-jammy

# Install Python for pytest runner and patch utility
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit (sparse checkout for java/)
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout c685486d68fb96745b47842972a5940d7e9acb14 && \
    git sparse-checkout init --cone && \
    git sparse-checkout set java/src/org/openqa/selenium java/test/org/openqa/selenium

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
