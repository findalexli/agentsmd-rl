FROM eclipse-temurin:17-jdk

# Install dependencies: python3 (for pytest), git, curl, and bazelisk
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install bazelisk
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Clone selenium repo at base commit
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git /workspace/selenium \
    && cd /workspace/selenium \
    && git checkout c685486d68fb96745b47842972a5940d7e9acb14

# Install pytest for test harness
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace/selenium

# Create log directory
RUN mkdir -p /logs/verifier

# Pre-fetch some bazel dependencies to speed up later
RUN bazel --version
