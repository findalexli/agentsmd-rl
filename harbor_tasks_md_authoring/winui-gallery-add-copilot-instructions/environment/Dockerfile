FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/winui-gallery && \
    cd /workspace/winui-gallery && \
    git remote add origin https://github.com/microsoft/WinUI-Gallery.git && \
    git fetch --depth=1 origin b7e044c155b011c275f0e20d774cfc1fe951b652 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/winui-gallery
