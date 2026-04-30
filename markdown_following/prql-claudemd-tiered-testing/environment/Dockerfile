FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pytest==8.3.4

WORKDIR /workspace
RUN git init /workspace/prql && \
    cd /workspace/prql && \
    git remote add origin https://github.com/PRQL/prql.git && \
    git fetch --depth=1 origin e125d11826e281f33e423519e403c7491a6fa24e && \
    git checkout FETCH_HEAD

WORKDIR /workspace/prql

RUN mkdir -p /logs/verifier
