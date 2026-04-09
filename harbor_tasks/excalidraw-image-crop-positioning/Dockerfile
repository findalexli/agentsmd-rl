FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest and dependencies
RUN pip3 install pytest pyyaml --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repo at base commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw

WORKDIR /workspace/excalidraw
# Checkout base commit before the fix
RUN git checkout f12ae80ba1e1364952c6c6c440ac4212acd06eab

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy test files
COPY tests/test_outputs.py /workspace/test_outputs.py
COPY tests/test.sh /workspace/test.sh
RUN chmod +x /workspace/test.sh

WORKDIR /workspace
