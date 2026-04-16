FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install python3 for pytest test harness
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Install pytest in venv
RUN pip install pytest

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout 76b61b943139741f3ea4adce5c6cfeb2e4ab8435

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
