# Selenium Grid Docker Stop Grace Period Task
FROM eclipse-temurin:17-jdk-jammy

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install bazelisk
RUN curl -L https://github.com/bazelbuild/bazelisk/releases/download/v1.19.0/bazelisk-linux-amd64 -o /usr/local/bin/bazel && \
    chmod +x /usr/local/bin/bazel

WORKDIR /workspace

# Clone selenium repo with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium

WORKDIR /workspace/selenium

# Checkout base commit (before PR fix)
RUN git checkout fbe388118cff80484638b724aaec3ee86c6eb0cd

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="$JAVA_HOME/bin:$PATH"
