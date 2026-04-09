FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
ARG BASE_COMMIT=c9cfcf888c0bf1021bd71da029301fedda71f6a9
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git && \
    cd selenium && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/selenium
