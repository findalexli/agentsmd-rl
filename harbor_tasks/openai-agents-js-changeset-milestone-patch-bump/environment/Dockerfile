FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv \
        && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git
WORKDIR /workspace/openai-agents-js
RUN git checkout f0ad7065c8ec8c532bf702d1912b7d42ee17b141

RUN mkdir -p /logs/verifier
