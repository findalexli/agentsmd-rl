FROM python:3.12-slim

# Install dependencies for Kotlin/Gradle build
RUN apt-get update && apt-get install -y \
    git \
    default-jdk \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Gradle
ENV GRADLE_VERSION=8.5
RUN wget https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip -O /tmp/gradle.zip \
    && unzip /tmp/gradle.zip -d /opt \
    && rm /tmp/gradle.zip

ENV GRADLE_HOME=/opt/gradle-${GRADLE_VERSION}
ENV PATH=${GRADLE_HOME}/bin:${PATH}

# Install Kotlin compiler
ENV KOTLIN_VERSION=1.9.22
RUN wget https://github.com/JetBrains/kotlin/releases/download/v${KOTLIN_VERSION}/kotlin-compiler-${KOTLIN_VERSION}.zip -O /tmp/kotlin.zip \
    && unzip /tmp/kotlin.zip -d /opt \
    && rm /tmp/kotlin.zip

ENV KOTLIN_HOME=/opt/kotlinc
ENV PATH=${KOTLIN_HOME}/bin:${PATH}

# Set up Java
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Create workspace directory
WORKDIR /workspace/kotlin

# Clone kotlin repository at base commit
ARG BASE_COMMIT=cf158c2f4a54d62787dc129cc1afdc86d08c9b9f
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git . \
    && git checkout ${BASE_COMMIT}

# Install pytest for test runner
RUN pip install pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Verify Java and Gradle installation
RUN java -version && gradle --version
