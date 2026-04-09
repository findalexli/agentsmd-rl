FROM eclipse-temurin:17-jdk-noble

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-pytest \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit
# Using shallow clone for efficiency
ARG BASE_COMMIT=49e930021babee259abbe37b4073305c96254b23
RUN git clone --filter=blob:none --depth 100 https://github.com/JetBrains/kotlin.git kotlin && \
    cd kotlin && \
    git fetch --depth=100 origin $BASE_COMMIT && \
    git checkout $BASE_COMMIT

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=$JAVA_HOME/bin:$PATH
ENV REPO=/workspace/kotlin

WORKDIR /workspace/kotlin
