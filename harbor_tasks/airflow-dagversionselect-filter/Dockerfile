FROM python:3.12-slim

# Install Node.js 22 and git
RUN apt-get update && apt-get install -y curl git && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone the Airflow repo at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git && \
    cd airflow && \
    git checkout 84010007d2e5553e2212ce4c63d4df063b8ebf4b

# Create verifier log directory
RUN mkdir -p /logs/verifier

# Set working directory to the UI project
WORKDIR /workspace/airflow/airflow-core/src/airflow/ui
