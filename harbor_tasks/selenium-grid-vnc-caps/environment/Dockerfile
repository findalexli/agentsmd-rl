FROM eclipse-temurin:21-jdk

# Install dependencies: python, git, curl, and build tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    curl \
    build-essential \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk (Bazel version manager)
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the repository at the base commit
ARG BASE_COMMIT=b1a7b8de7bf8c9889627914888adee44c01f925a
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/selenium
