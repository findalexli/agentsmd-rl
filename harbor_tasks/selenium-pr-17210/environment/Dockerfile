FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit
ARG BASE_COMMIT=6ce07dbfaca9ff0146dcaed9315c9fe8d1b0a03f
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git && \
    cd selenium && \
    git checkout ${BASE_COMMIT}

# Pre-install/build dependencies if any
WORKDIR /workspace/selenium

# Ensure logs directory exists
RUN mkdir -p /logs/verifier
