# Dockerfile for Selenium Grid NodeCommandInterceptor task
FROM eclipse-temurin:17-jdk-jammy

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    python3 \
    python3-pip \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk (which handles Bazel version management)
RUN curl -Lo /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/download/v1.19.0/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel

# Create directories
RUN mkdir -p /logs/verifier /workspace

WORKDIR /workspace

# Clone the repository at base commit with blobless filter
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 6e3625b180bd8a3ef95df32ee44befd715568dc6

# Pre-fetch Bazel dependencies for the specific target to speed up tests
WORKDIR /workspace/selenium

# Create .bazelrc for better performance
RUN echo "build --jobs=4" >> .bazelrc.user \
    && echo "build --local_cpu_resources=4" >> .bazelrc.user \
    && echo "test --test_output=errors" >> .bazelrc.user

# Set working directory
WORKDIR /workspace/selenium
