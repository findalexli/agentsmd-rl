FROM node:22-slim

RUN apt-get update && apt-get install -y ca-certificates git python3 python3-pip python3-venv --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install pytest==8.3.4 pyyaml==6.0.2

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js

WORKDIR /workspace/openai-agents-js

RUN git checkout 41c1b89f650a9d18aeb76677f965dcfb06087c90

RUN mkdir -p /logs/verifier
