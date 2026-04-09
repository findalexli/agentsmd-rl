FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python3, pip and venv for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the Selenium repository at base commit
# Use --depth to reduce clone size since we only need specific commit
RUN git clone --filter=blob:none --depth=100 https://github.com/SeleniumHQ/selenium.git selenium

WORKDIR /workspace/selenium

# Checkout the base commit
RUN git checkout f455679160058286ff6a6926923110c32a3b283d

# Initialize submodules if needed
RUN git submodule update --init --recursive || true

# Set up Python virtual environment and install pytest
RUN python3 -m venv /workspace/venv && \
    /workspace/venv/bin/pip install pytest

# Ensure logs directory exists for verifier
RUN mkdir -p /logs/verifier
