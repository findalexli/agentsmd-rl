FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install python3 for pytest test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the selenium repo at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout 1dc4a61843346508c0464bab596b867e7e389966

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the dotnet source
WORKDIR /workspace/selenium/dotnet/src/webdriver
