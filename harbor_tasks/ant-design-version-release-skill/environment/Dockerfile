FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-report==1.5.0 \
    pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git /workspace/ant-design \
    && cd /workspace/ant-design \
    && git checkout 75feea4c5543ef2dc68f7832c2774d592fe4a032

WORKDIR /workspace/ant-design

RUN mkdir -p /logs/verifier
