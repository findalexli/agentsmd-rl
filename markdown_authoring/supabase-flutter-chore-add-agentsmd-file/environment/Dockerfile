FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/supabase-flutter && \
    cd /workspace/supabase-flutter && \
    git remote add origin https://github.com/supabase/supabase-flutter.git && \
    git fetch --depth=1 origin 8e0993c64cbb7f7aaaa6b989c85a26ac7249f884 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/supabase-flutter
