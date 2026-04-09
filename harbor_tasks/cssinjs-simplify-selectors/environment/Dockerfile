FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest --break-system-packages

RUN mkdir -p /workspace/ant-design /logs/verifier

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git && \
    cd ant-design && \
    git checkout a3aa5bc3a348df4c3091d0095e2685c140b786b8

WORKDIR /workspace/ant-design

# Install dependencies
RUN npm install

# Copy test files
COPY tests/test_outputs.py /workspace/ant-design/test_outputs.py
COPY tests/test.sh /workspace/ant-design/test.sh
