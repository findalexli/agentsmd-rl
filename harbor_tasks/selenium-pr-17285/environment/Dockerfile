# Selenium .NET BiDi Input Actions Refactor Task
FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repository at base commit (parent of merge)
# Using filter=blob:none for faster clone
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout 4a4c5939467b98db4c16f40f6d3c26626964c91b

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/selenium
