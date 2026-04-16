FROM python:3.12-slim

# Install Java (Kotlin compiler needs JDK)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    openjdk-21-jdk \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Kotlin compiler
ENV KOTLIN_VERSION=2.0.21
RUN curl -L "https://github.com/JetBrains/kotlin/releases/download/v${KOTLIN_VERSION}/kotlin-compiler-${KOTLIN_VERSION}.zip" -o /tmp/kotlin.zip \
    && unzip /tmp/kotlin.zip -d /opt/ \
    && rm /tmp/kotlin.zip

ENV PATH="/opt/kotlinc/bin:${PATH}"
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

# Set up workspace
WORKDIR /workspace

# Clone the Kotlin repository at base commit (shallow clone for speed)
ARG REPO_URL=https://github.com/JetBrains/kotlin.git
ARG BASE_COMMIT=56dd547ef4b6c5339be9b3cbbdf0b208acdcf9fb

RUN git clone --filter=blob:none --no-checkout "${REPO_URL}" kotlin && \
    cd kotlin && \
    git sparse-checkout init && \
    git sparse-checkout set \
        "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/" \
        "plugins/compose/compiler-hosted/build.gradle.kts" \
        "build.gradle.kts" \
        "gradle/" \
        "gradlew" \
        "settings.gradle.kts" \
        "gradle.properties" \
        ".gradle/" 2>/dev/null || true && \
    git fetch --depth=1 origin "${BASE_COMMIT}" && \
    git checkout "${BASE_COMMIT}"

WORKDIR /workspace/kotlin

# Pre-download Gradle wrapper and dependencies
RUN ./gradlew --version 2>/dev/null || true

# Create log directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
