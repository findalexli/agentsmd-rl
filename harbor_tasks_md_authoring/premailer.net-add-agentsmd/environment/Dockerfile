FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/premailer.net && \
    cd /workspace/premailer.net && \
    git remote add origin https://github.com/milkshakesoftware/PreMailer.Net.git && \
    git fetch --depth=1 origin ab75f9c389f671bb9fbcac75e5cb30e4ca503492 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/premailer.net
