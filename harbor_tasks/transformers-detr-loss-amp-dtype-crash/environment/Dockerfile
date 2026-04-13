FROM node:18-slim

WORKDIR /workspace/express-async-handler

# Install Python and other dependencies for testing
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Install TypeScript and ts-node for code execution
RUN npm install -g typescript ts-node

# Copy the mock repo content (from parent directory context)
COPY repo/ .

# Install dependencies
RUN npm install

# Copy tests (from parent directory context)
COPY tests/test_outputs.py /tests/test_outputs.py
COPY tests/test.sh /tests/test.sh
RUN chmod +x /tests/test.sh

WORKDIR /workspace/express-async-handler
