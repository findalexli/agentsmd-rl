FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        grep \
        unzip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

# Install bun from a pinned GitHub release (v1.1.42 for linux x64)
RUN curl -fsSLo /tmp/bun.zip \
        https://github.com/oven-sh/bun/releases/download/bun-v1.1.42/bun-linux-x64.zip \
    && cd /usr/local/bin && unzip -q -o -j /tmp/bun.zip \
    && rm /tmp/bun.zip \
    && chmod +x /usr/local/bin/bun

WORKDIR /workspace

RUN git init /workspace/prql && \
    cd /workspace/prql && \
    git remote add origin https://github.com/PRQL/prql.git && \
    git fetch --depth=1 origin 541974b371bac89e3c7e758106ecde97df307f4c && \
    git checkout FETCH_HEAD

# Install grammar dependencies so CI-derived tests pass out of the box
RUN cd /workspace/prql/grammars/prql-lezer && bun install && rm -f bun.lockb

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prql
