FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    openjdk-17-jdk \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Kotlin command line tools
RUN curl -L -o kotlin-compiler.zip https://github.com/JetBrains/kotlin/releases/download/v2.0.20/kotlin-compiler-2.0.20.zip && \
    unzip kotlin-compiler.zip -d /opt/ && \
    rm kotlin-compiler.zip

ENV PATH="/opt/kotlinc/bin:${PATH}"
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Clone the Kotlin repository at base commit
ARG BASE_COMMIT=3325ebdb5efefe65d4f4e93540ffc010e3db8055
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git /workspace/kotlin && \
    cd /workspace/kotlin && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/kotlin

# Pre-download Gradle wrapper and some dependencies to speed up testing
RUN ./gradlew --version 2>/dev/null || true

RUN mkdir -p /logs/verifier

# Copy test files
COPY tests/test_outputs.py /workspace/test_outputs.py
COPY solution/solve.sh /workspace/solve.sh
RUN chmod +x /workspace/solve.sh

WORKDIR /workspace
