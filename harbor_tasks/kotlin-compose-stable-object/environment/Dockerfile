FROM python:3.12-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Kotlin command line tools (for basic validation)
RUN curl -L -o /tmp/kotlin.zip https://github.com/JetBrains/kotlin/releases/download/v2.1.0/kotlin-compiler-2.1.0.zip \
    && unzip /tmp/kotlin.zip -d /opt/ \
    && rm /tmp/kotlin.zip

ENV PATH="/opt/kotlinc/bin:${PATH}"

# Clone the Kotlin repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git kotlin \
    && cd kotlin \
    && git checkout 6030128bf5943db6bda17fb603eadcd5214064cd

# Setup log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
