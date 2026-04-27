FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git openai-agents-js \
    && cd openai-agents-js \
    && git checkout b54fc4a3222ea8b14b1c3a8e45457b4905354bee

RUN mkdir -p /logs/verifier
