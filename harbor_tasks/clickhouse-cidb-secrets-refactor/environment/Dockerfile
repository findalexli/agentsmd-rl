FROM python:3.12-slim

RUN apt-get update && apt-get install -y     git     && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone ClickHouse repo and checkout base commit
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse &&     cd /workspace/ClickHouse &&     git checkout bc855b917b3f456bfd6198c5bc29a1bc5672aabf
