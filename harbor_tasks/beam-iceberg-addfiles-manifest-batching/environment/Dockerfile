FROM eclipse-temurin:11-jdk-jammy

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV GRADLE_OPTS="-Xmx4g -Dorg.gradle.daemon=false"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone for large monorepo)
RUN git clone --filter=blob:none https://github.com/apache/beam.git /workspace/beam && \
    cd /workspace/beam && \
    git checkout d6e04d11c64c70b30916a86303a6d3e3db746073 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# Pre-compile iceberg module to cache Gradle wrapper + all dependencies + build artifacts.
# This makes incremental compilation during tests much faster.
RUN ./gradlew :sdks:java:io:iceberg:compileJava --no-daemon 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
