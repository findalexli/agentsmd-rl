FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/prql && \
    cd /workspace/prql && \
    git remote add origin https://github.com/PRQL/prql.git && \
    git fetch --depth=1 origin ab89a8b6b4afbe26ddf8d2ebb040470fea5a7a47 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prql
