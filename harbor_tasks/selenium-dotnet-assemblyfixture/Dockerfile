FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the selenium repo at the base commit
# Using shallow clone for efficiency since we only need specific files
ARG BASE_COMMIT=d8fe629eec05f31dd498ac49c2ddde02be2b9f10
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git && \
    cd selenium && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/selenium
