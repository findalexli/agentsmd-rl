FROM python:3.12-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    default-jdk \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set up Java
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Clone Kotlin repository at base commit (shallow clone for faster build)
WORKDIR /workspace
RUN git clone --filter=blob:none --depth=1 https://github.com/JetBrains/kotlin.git kotlin

WORKDIR /workspace/kotlin
# Fetch the base commit and checkout
RUN git fetch --depth=1 origin 2a4c65fb2b7a8f7d50235c12145e07f1b8ffbf78 && \
    git checkout 2a4c65fb2b7a8f7d50235c12145e07f1b8ffbf78

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
