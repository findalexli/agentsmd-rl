FROM ubuntu:24.04

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    openjdk-21-jdk \
    && rm -rf /var/lib/apt-get/lists/*

# Set up Python
RUN python3 -m pip install --break-system-packages pytest pyyaml

# Set working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit
# Using shallow clone for efficiency
RUN git init /workspace/kotlin && \
    cd /workspace/kotlin && \
    git remote add origin https://github.com/JetBrains/kotlin.git && \
    git fetch --depth=1 origin e3b4d7fe1cccf74f80f8ea53d9332a2c6e657f8f && \
    git checkout FETCH_HEAD

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"
