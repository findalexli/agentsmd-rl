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
    git fetch --depth=1 origin bb6dc5c1148a7c30af1ec372aad8698427bc0424 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openvino.genai
