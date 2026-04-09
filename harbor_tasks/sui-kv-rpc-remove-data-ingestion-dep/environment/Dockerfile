FROM rust:1.85-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at base commit (shallow clone for speed)
RUN git clone --depth=1 --branch main https://github.com/MystenLabs/sui.git sui

WORKDIR /workspace/sui

# Fetch the specific base commit
RUN git fetch --depth=1 origin 80af79ea6b5e18a23042fc7bda481e07472c7a8d && \
    git checkout 80af79ea6b5e18a23042fc7bda481e07472c7a8d

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
