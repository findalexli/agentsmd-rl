FROM eclipse-temurin:17-jdk

# Install dependencies: git, python3, curl
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
ARG REPO_URL=https://github.com/JetBrains/kotlin.git
ARG BASE_COMMIT=3657c00274a9252a8b71e6434cd6c63cf3770803

RUN git clone --filter=blob:none --depth=1 $REPO_URL kotlin && \
    cd kotlin && \
    git fetch --depth=1 origin $BASE_COMMIT && \
    git checkout $BASE_COMMIT

# Verify the target file exists
RUN ls -la /workspace/kotlin/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
