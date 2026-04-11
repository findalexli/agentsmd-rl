FROM php:8.3-cli

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repository at base commit
ARG REPO_SHORT=appwrite
ARG BASE_COMMIT=3ed1ca736dd2889b675775687e58db041283ad5a
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git ${REPO_SHORT}
WORKDIR /workspace/${REPO_SHORT}
RUN git checkout ${BASE_COMMIT}

# Set up Python environment for tests
WORKDIR /workspace
RUN python3 -m venv /workspace/.venv
ENV PATH="/workspace/.venv/bin:$PATH"
RUN pip install --upgrade pip pytest pyyaml

# Copy test files
COPY tests/test_outputs.py /workspace/tests/
COPY solution/solve.sh /workspace/solution/

# Create fixed test.sh that properly writes reward file
RUN cat > /workspace/tests/test.sh << 'EOF'
#!/bin/bash

# Install pytest if needed
pip install pytest pyyaml 2>/dev/null || true

# Run the verifier tests
cd /workspace
python -m pytest tests/test_outputs.py -v --tb=short
exit_code=$?

# Write binary reward for the harness (reward, not reward.txt)
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
EOF
RUN chmod +x /workspace/tests/test.sh

WORKDIR /workspace
