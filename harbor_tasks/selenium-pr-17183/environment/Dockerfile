# Dockerfile for selenium-execute-method-backward-compat task
FROM eclipse-temurin:21-jdk-jammy

# Install Python for pytest test harness + git + utilities
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone Selenium repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout cc496f59bd9807fb16e0c7f5b51b1d376e2fb874

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/selenium
