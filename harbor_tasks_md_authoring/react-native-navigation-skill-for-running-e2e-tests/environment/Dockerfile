FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/react-native-navigation && \
    cd /workspace/react-native-navigation && \
    git remote add origin https://github.com/wix/react-native-navigation.git && \
    git fetch --depth=1 origin f8a416d3ebaa4c024d195a811c504d1872f12620 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/react-native-navigation
