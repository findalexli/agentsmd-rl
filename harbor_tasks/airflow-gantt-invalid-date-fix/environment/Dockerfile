FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone airflow repo at base commit
ARG BASE_COMMIT=a06896fe1de2213b5c1c2d07c8310f4a85ea507c
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout ${BASE_COMMIT}

# Set working directory to the UI package
WORKDIR /workspace/airflow/airflow-core/src/airflow/ui

# Install dependencies
RUN npm install -g pnpm && \
    pnpm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
