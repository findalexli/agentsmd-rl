# Selenium Java Lazy class RuntimeException fix task
FROM eclipse-temurin:17-jdk-jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir pytest

WORKDIR /workspace

# Clone Selenium repo at base commit (before fix)
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 4bb23f484eec6f986b563fb3146cb64dcbcc0187

# Create test directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
