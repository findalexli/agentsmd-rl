FROM ubuntu:22.04

# Install required tools: OpenJDK, git, python3 for pytest, and gradle for building
RUN apt-get update && apt-get install -y \
    openjdk-21-jdk \
    git \
    python3 \
    python3-pip \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Gradle 8.5 (commonly used for Kotlin projects)
RUN curl -L https://services.gradle.org/distributions/gradle-8.5-bin.zip -o gradle.zip && \
    unzip gradle.zip && \
    mv gradle-8.5 /opt/gradle && \
    rm gradle.zip
ENV PATH="/opt/gradle/bin:${PATH}"

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the Kotlin repository at the base commit (shallow clone with filter)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git checkout 363c7068258ef79a8e174bd7ca48209be4c0e29c

WORKDIR /workspace/kotlin
