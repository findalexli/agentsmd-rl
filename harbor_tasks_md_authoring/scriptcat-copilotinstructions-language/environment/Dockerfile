FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/scriptcat && \
    cd /workspace/scriptcat && \
    git remote add origin https://github.com/scriptscat/scriptcat.git && \
    git fetch --depth=1 origin dd64da719c081acbf21645e2b1e1f38653ffae8c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/scriptcat
