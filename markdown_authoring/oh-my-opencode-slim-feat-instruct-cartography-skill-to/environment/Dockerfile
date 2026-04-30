FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/oh-my-opencode-slim && \
    cd /workspace/oh-my-opencode-slim && \
    git remote add origin https://github.com/alvinunreal/oh-my-opencode-slim.git && \
    git fetch --depth=1 origin acc366318b7c6572106be42a621ec5a03e265191 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/oh-my-opencode-slim
