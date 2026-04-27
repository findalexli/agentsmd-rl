FROM node:24-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix \
    && cd /workspace/remix \
    && git checkout bf2a74b63184ec2da7fbe993fd12e229a42fb3f1 \
    && git config user.email "task@example.com" \
    && git config user.name "Task"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/remix
