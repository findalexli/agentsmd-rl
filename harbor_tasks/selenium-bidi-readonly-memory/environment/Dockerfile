FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages --quiet

# Set up working directory
WORKDIR /workspace/selenium

# Clone the repo at base commit with shallow history for speed
ARG BASE_COMMIT=c9cfcf888c0bf1021bd71da029301fedda71f6a9
RUN git clone --filter=blob:none --depth=100 https://github.com/SeleniumHQ/selenium.git . && \
    git checkout ${BASE_COMMIT}

# Pre-restore NuGet packages for faster builds
WORKDIR /workspace/selenium/dotnet
RUN dotnet restore src/webdriver/Selenium.WebDriver.csproj 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
