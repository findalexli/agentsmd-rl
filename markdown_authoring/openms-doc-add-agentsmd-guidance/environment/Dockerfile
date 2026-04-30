FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openms && \
    cd /workspace/openms && \
    git remote add origin https://github.com/OpenMS/OpenMS.git && \
    git fetch --depth=1 origin 7977ca7e50b60eb03fd28289dbf4a8e2b5beae76 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openms
