FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_OPTIONS=--max-old-space-size=8192
ENV CI=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design \
    && cd ant-design \
    && git fetch --depth 1 origin 1c5cf81d07981cfa7a826702a1703adc414a4921 \
    && git checkout 1c5cf81d07981cfa7a826702a1703adc414a4921

WORKDIR /workspace/ant-design

RUN npm install --ignore-scripts --no-audit --no-fund --legacy-peer-deps

RUN npx dumi setup

RUN mkdir -p /logs/verifier
