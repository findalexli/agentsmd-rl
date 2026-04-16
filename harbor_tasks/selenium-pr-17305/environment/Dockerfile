# Selenium .NET DevTools lazy initialization task
FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install python3 and pytest for test runner
RUN apt-get update && apt-get install -y python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install pytest --break-system-packages

# Clone Selenium repo at base commit (sparse checkout for dotnet only)
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git sparse-checkout init --cone && \
    git sparse-checkout set dotnet && \
    git checkout e78c3900fdef5d729cc3a24cfc7e2e7ea3421de4

WORKDIR /workspace/selenium

# Create logs directory
RUN mkdir -p /logs/verifier
