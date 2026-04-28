FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/prairielearn && \
    cd /workspace/prairielearn && \
    git remote add origin https://github.com/PrairieLearn/PrairieLearn.git && \
    git fetch --depth=1 origin 17d74207e5fd73c26bb240e1cf83fa64601909fc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prairielearn
