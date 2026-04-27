FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design \
    && cd ant-design \
    && git checkout 62135b4b76d5a85b662d9f8b1fb57fcbbe4795d6

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
