FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/storybook && \
    cd /workspace/storybook && \
    git remote add origin https://github.com/storybookjs/storybook.git && \
    git fetch --depth=1 origin 512098b0a9e05fe75a096a2fdc1ee4e41a0acbaf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/storybook
