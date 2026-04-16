# Selenium .NET WebDriver build environment
FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Clone repo with sparse checkout for dotnet only
WORKDIR /workspace
RUN git clone --filter=blob:none --sparse https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git sparse-checkout set dotnet common \
    && git checkout 1d58a30530101d6ff84ecabb4422ac3078f8e40d

WORKDIR /workspace/selenium

# Create logs directory
RUN mkdir -p /logs/verifier
