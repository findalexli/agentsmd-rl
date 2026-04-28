FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openvino.genai && \
    cd /workspace/openvino.genai && \
    git remote add origin https://github.com/openvinotoolkit/openvino.genai.git && \
    git fetch --depth=1 origin b2bfa5b0ba62aceae21cd85eb6c17e59acf7644e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openvino.genai
