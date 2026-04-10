FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install required dependencies including git, curl, and other build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        wget unzip xz-utils file && \
    rm -rf /var/lib/apt/lists/*

# Install Flutter SDK (use a newer version with Dart 3.6.0+)
ENV FLUTTER_VERSION=3.27.0
ENV FLUTTER_HOME=/opt/flutter
ENV PATH="${FLUTTER_HOME}/bin:${PATH}"

RUN git clone --depth=1 --branch ${FLUTTER_VERSION} https://github.com/flutter/flutter.git ${FLUTTER_HOME} && \
    ${FLUTTER_HOME}/bin/flutter doctor && \
    ${FLUTTER_HOME}/bin/flutter config --no-analytics && \
    ${FLUTTER_HOME}/bin/flutter precache

# Clone the repo at the base commit
RUN git clone --filter=blob:none https://github.com/matthiasn/lotti.git /workspace/lotti && \
    cd /workspace/lotti && \
    git checkout be8bbfc8f59d502773f05d99b835f122c22b18c1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lotti

# Pre-fetch Flutter dependencies to make tests faster and avoid analyze errors
RUN flutter pub get || true

RUN mkdir -p /logs/verifier
