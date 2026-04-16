FROM eclipse-temurin:17-jdk

# Install dependencies: git, curl, python3, and gradle dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Kotlin compiler
RUN curl -L -o /tmp/kotlin-compiler.zip https://github.com/JetBrains/kotlin/releases/download/v2.2.0/kotlin-compiler-2.2.0.zip && \
    unzip /tmp/kotlin-compiler.zip -d /opt && \
    rm /tmp/kotlin-compiler.zip && \
    ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc && \
    ln -s /opt/kotlinc/bin/kotlin /usr/local/bin/kotlin

# Set up working directory
WORKDIR /workspace

# Clone the kotlin repository at base commit with shallow clone
ARG BASE_COMMIT=b9b226ad3ced5c05afd2d6c8b31f7352bfd7c2d2
RUN git clone --depth=100 --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/kotlin
