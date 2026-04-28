FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/stripe-react-native && \
    cd /workspace/stripe-react-native && \
    git remote add origin https://github.com/stripe/stripe-react-native.git && \
    git fetch --depth=1 origin 9e8bc41188a7a45df6ccc06a8ad237a0502807e5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/stripe-react-native
