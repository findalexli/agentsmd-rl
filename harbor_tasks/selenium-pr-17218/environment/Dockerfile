FROM eclipse-temurin:17-jdk-jammy

# Install essential tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone the Selenium repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 491207a87b89b2824d8ca976fa7cb46cce9325ea

# Set up working directory
WORKDIR /workspace/selenium

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
