FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/chatgptbox && \
    cd /workspace/chatgptbox && \
    git remote add origin https://github.com/ChatGPTBox-dev/chatGPTBox.git && \
    git fetch --depth=1 origin 3768a06dc3eee3651cbc9ee061bf4e7892827dfc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/chatgptbox
