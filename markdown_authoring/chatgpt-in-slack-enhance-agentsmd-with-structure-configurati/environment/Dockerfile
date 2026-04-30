FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/chatgpt-in-slack && \
    cd /workspace/chatgpt-in-slack && \
    git remote add origin https://github.com/seratch/ChatGPT-in-Slack.git && \
    git fetch --depth=1 origin 5b062896065ba6df5cada8de267ebb6ad6fe4784 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/chatgpt-in-slack
