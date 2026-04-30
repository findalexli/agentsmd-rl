FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        ca-certificates \
        bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

WORKDIR /workspace
RUN git init /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin 05dd513231c04ffb6013a25118605a7a72a9a063 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/openai-agents-js

RUN mkdir -p /logs/verifier
