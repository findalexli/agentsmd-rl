FROM eclipse-temurin:21-jdk

# Install dependencies: git, python3, pip
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Gradle (version 8.5 for Kotlin project compatibility)
RUN curl -L https://services.gradle.org/distributions/gradle-8.5-bin.zip -o gradle.zip \
    && unzip gradle.zip \
    && mv gradle-8.5 /opt/gradle \
    && rm gradle.zip
ENV PATH="/opt/gradle/bin:${PATH}"

# Install pytest
RUN pip3 install pytest --break-system-packages

# Setup workspace
WORKDIR /workspace

# Clone the Kotlin repository at base commit (shallow clone for speed)
ARG REPO=https://github.com/JetBrains/kotlin.git
ARG BASE_COMMIT=731ea08ab113c6d87abdb9d5d6f10299d4547395

RUN git clone --depth 100 --filter=blob:none ${REPO} kotlin \
    && cd kotlin \
    && git fetch --depth 100 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
