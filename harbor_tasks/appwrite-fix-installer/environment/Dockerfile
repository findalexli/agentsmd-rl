FROM php:8.3-cli-bookworm

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        patch \
        && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git /workspace/appwrite \
    && cd /workspace/appwrite \
    && git checkout ea032c28046c9f6cb1c2801fa80a9111f7e5fcd1

RUN mkdir -p /logs/verifier
