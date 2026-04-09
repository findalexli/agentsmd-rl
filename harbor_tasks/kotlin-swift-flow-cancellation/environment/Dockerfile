FROM python:3.12-slim

# Install git, JDK, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    default-jdk \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the Kotlin repository at base commit (shallow clone with filter for speed)
ENV REPO=kotlin
ENV BASE_COMMIT=aa96b1eb9878f7e427671338882cd24dc514a090

RUN git clone --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
