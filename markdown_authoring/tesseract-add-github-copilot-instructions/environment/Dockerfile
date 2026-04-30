FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tesseract && \
    cd /workspace/tesseract && \
    git remote add origin https://github.com/tesseract-ocr/tesseract.git && \
    git fetch --depth=1 origin a6dac7d31700b0b5c2efe1c87716b194d9d474a4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tesseract
