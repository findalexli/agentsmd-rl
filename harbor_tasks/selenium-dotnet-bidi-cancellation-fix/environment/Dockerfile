FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python and dependencies needed by test harness
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=b6a1ff4dcea3f83f45bf10cbe20ea2f9c29469d4
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium && \
    cd selenium && \
    git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

# Set up Python for test harness
WORKDIR /workspace/task
