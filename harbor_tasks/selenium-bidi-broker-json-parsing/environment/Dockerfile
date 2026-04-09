FROM mcr.microsoft.com/dotnet/sdk:8.0

# Install Python for test runner and Bazel (Bazelisk)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Bazelisk
RUN npm install -g @bazel/bazelisk && ln -sf $(which bazelisk) /usr/local/bin/bazel

# Set working directory
WORKDIR /workspace

# Clone selenium repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=87db23284dceb224d13a13c4b72da5a2e6b7f21a
RUN git clone --depth 100 --filter=blob:none https://github.com/SeleniumHQ/selenium.git && \
    cd selenium && \
    git fetch --depth 100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install pytest for test runner
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
