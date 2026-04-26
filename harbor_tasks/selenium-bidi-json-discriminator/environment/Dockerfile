FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/SeleniumHQ/selenium.git && \
    git fetch --depth=1 origin 5c2bf6b42fb66f895d936cf13a392385fb032689 && \
    git checkout FETCH_HEAD

# Verify the target file exists
RUN ls -la /workspace/selenium/dotnet/src/webdriver/BiDi/Json/

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
