FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python and required tools for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the selenium repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=e78c3900fdef5d729cc3a24cfc7e2e7ea3421de4
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/SeleniumHQ/selenium.git && \
    git fetch --depth=1 origin e78c3900fdef5d729cc3a24cfc7e2e7ea3421de4 && \
    git checkout FETCH_HEAD

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
