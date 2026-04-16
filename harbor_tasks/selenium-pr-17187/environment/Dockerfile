FROM eclipse-temurin:17-jdk-jammy

# Install Python for pytest runner, basic tools, and build dependencies for Bazel
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    curl \
    build-essential \
    gcc \
    g++ \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk
RUN curl -fsSL -o /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/download/v1.19.0/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

WORKDIR /workspace

# Clone Selenium repo at base commit
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 7cebc1065fd21fb3cd2613ab94600eb69e019e6f

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
