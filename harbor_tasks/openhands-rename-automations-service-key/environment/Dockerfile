FROM python:3.12-slim

WORKDIR /workspace

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git openhands \
    && cd openhands \
    && git fetch --depth=1 origin 3516c3cdbe4e3713e7e1bb9b3b5041c281f29f0a \
    && git checkout 3516c3cdbe4e3713e7e1bb9b3b5041c281f29f0a

WORKDIR /workspace/openhands

# Install enterprise dependencies
RUN cd enterprise && pip install fastapi pydantic pytest pytest-asyncio httpx --no-cache-dir

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
