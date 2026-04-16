# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Kotlin compiler
RUN curl -L "https://github.com/JetBrains/kotlin/releases/download/v2.1.0/kotlin-compiler-2.1.0.zip" -o /tmp/kotlin.zip && \
    unzip /tmp/kotlin.zip -d /opt/ && \
    rm /tmp/kotlin.zip && \
    ln -s /opt/kotlinc/bin/kotlin /usr/local/bin/kotlin && \
    ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc

# Clone Kotlin repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout 731ea08ab113c6d87abdb9d5d6f10299d4547395

# Install pytest
RUN pip install --no-cache-dir pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
