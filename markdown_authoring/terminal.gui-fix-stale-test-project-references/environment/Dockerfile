FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/terminal.gui && \
    cd /workspace/terminal.gui && \
    git remote add origin https://github.com/gui-cs/Terminal.Gui.git && \
    git fetch --depth=1 origin 052d5c0b0a36a50fa64f6667cc25c382a4b21b38 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/terminal.gui
