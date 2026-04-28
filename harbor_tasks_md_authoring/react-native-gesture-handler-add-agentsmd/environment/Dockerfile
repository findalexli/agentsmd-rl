FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/react-native-gesture-handler && \
    cd /workspace/react-native-gesture-handler && \
    git remote add origin https://github.com/software-mansion/react-native-gesture-handler.git && \
    git fetch --depth=1 origin fd14d128ba9adbd5043490d252573acae7f946fc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/react-native-gesture-handler
