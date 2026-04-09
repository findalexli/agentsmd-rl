FROM openjdk:17-jdk-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the Kotlin repository at the base commit
ARG BASE_COMMIT
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables
ENV JAVA_HOME=/usr/local/openjdk-17
ENV PATH=$PATH:$JAVA_HOME/bin
