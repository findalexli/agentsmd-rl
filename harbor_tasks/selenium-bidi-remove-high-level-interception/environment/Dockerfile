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

# Clone the selenium repo at base commit
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout f455679160058286ff6a6926923110c32a3b283d

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
