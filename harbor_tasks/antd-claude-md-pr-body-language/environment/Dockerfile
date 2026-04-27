FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

RUN git init ant-design \
    && cd ant-design \
    && git remote add origin https://github.com/ant-design/ant-design.git \
    && git fetch --depth=1 origin 07f63a6df00dcf32f855a00ca6fe818053dca0c3 \
    && git checkout FETCH_HEAD \
    && git config --global user.email "task@example.com" \
    && git config --global user.name "task"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
