FROM python:3.12-slim

# Install Java and basic tools needed for Kotlin/Gradle
RUN apt-get update && apt-get install -y \
    git \
    openjdk-21-jdk \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Create directory structure for tests
RUN mkdir -p /workspace/task && ln -s /tests /workspace/task/tests

# Clone the Kotlin repository at base commit
ARG BASE_COMMIT=4dacdd37f64ec8643eea5b22f12a8256e7b5ced9
RUN git clone --filter=blob:none --depth=100 https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/kotlin
