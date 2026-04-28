FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/quran.com-frontend-next && \
    cd /workspace/quran.com-frontend-next && \
    git remote add origin https://github.com/quran/quran.com-frontend-next.git && \
    git fetch --depth=1 origin 0b3e5dcf9fcabef6d651f4146351225a83aa4af5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/quran.com-frontend-next
