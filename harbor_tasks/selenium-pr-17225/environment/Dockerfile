FROM eclipse-temurin:21-jdk-jammy

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone Selenium repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout 1303596bccafc9f39708d8ac61b52424c7d00394

# Download jspecify dependency needed for compilation
RUN mkdir -p /workspace/libs && \
    curl -sL -o /workspace/libs/jspecify-1.0.0.jar \
    https://repo1.maven.org/maven2/org/jspecify/jspecify/1.0.0/jspecify-1.0.0.jar

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
