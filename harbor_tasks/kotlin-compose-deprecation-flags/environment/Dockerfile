FROM python:3.12-slim

# Install Java, Kotlin, and Git
RUN apt-get update && apt-get install -y \
    git \
    openjdk-21-jdk \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Kotlin compiler
RUN wget -q https://github.com/JetBrains/kotlin/releases/download/v2.1.0/kotlin-compiler-2.1.0.zip \
    && unzip -q kotlin-compiler-2.1.0.zip -d /opt \
    && rm kotlin-compiler-2.1.0.zip

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV KOTLIN_HOME=/opt/kotlinc
ENV PATH="${KOTLIN_HOME}/bin:${JAVA_HOME}/bin:${PATH}"

# Clone the Kotlin repository at base commit
WORKDIR /workspace
ARG BASE_COMMIT=f94fe0faca67ca5a57db9421948cab80af1686b7
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin \
    && cd kotlin \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Setup working directory
WORKDIR /workspace/kotlin

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-warm Gradle by downloading wrapper (this speeds up subsequent builds)
RUN ./gradlew --version || true

# Create gradle.properties to speed up builds
RUN echo "org.gradle.daemon=false" >> /root/.gradle/gradle.properties \
    && echo "org.gradle.parallel=true" >> /root/.gradle/gradle.properties \
    && echo "org.gradle.configureondemand=true" >> /root/.gradle/gradle.properties \
    && echo "org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g" >> /root/.gradle/gradle.properties

WORKDIR /workspace/kotlin
