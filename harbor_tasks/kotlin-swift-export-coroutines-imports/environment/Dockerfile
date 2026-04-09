FROM eclipse-temurin:21-jdk

# Install dependencies: git, python3, pip
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=ff1ea74e2d4c120495571a5b32d7075a9e8dba07
RUN git clone --depth=100 --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/kotlin
