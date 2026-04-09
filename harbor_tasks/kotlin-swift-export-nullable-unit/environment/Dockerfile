FROM python:3.12-slim-bookworm

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone Kotlin repository with shallow history
# Need to fetch enough history to get the base commit
RUN git clone --depth=100 https://github.com/JetBrains/kotlin.git kotlin

# Checkout the base commit
RUN cd kotlin && \
    git fetch --depth=50 origin 2e2f6a81403366bb2c15c300005f637de413319e && \
    git checkout 2e2f6a81403366bb2c15c300005f637de413319e

# Set Java home
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
