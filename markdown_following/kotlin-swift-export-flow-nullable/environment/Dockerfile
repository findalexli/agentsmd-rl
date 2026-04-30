FROM swift:6.0-jammy

# Install required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Kotlin compiler
RUN curl -L https://github.com/JetBrains/kotlin/releases/download/v2.1.0/kotlin-compiler-2.1.0.zip -o /tmp/kotlin.zip \
    && unzip /tmp/kotlin.zip -d /opt/ \
    && rm /tmp/kotlin.zip

ENV PATH="/opt/kotlinc/bin:${PATH}"

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone Kotlin repo at base commit
# Using a shallow clone with specific commit
RUN git init /workspace/kotlin && \
    cd /workspace/kotlin && \
    git remote add origin https://github.com/JetBrains/kotlin.git && \
    git fetch --depth=1 origin e3b4d7fe1cccf74f80f8ea53d9332a2c6e657f8f && \
    git checkout FETCH_HEAD

WORKDIR /workspace/kotlin
