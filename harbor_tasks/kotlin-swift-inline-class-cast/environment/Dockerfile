FROM eclipse-temurin:17-jdk

# Install Python and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set Java environment
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Clone Kotlin repository at base commit (shallow clone for speed)
WORKDIR /workspace
ARG BASE_COMMIT=e5bfbbbd7f9d48f9d6039cd7d9459719d02b9b30
RUN git clone --depth=200 --filter=blob:none https://github.com/JetBrains/kotlin.git && \
    cd kotlin && \
    git fetch --depth=200 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/kotlin

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-download Gradle wrapper dependencies to speed up tests
RUN ./gradlew --version || true
