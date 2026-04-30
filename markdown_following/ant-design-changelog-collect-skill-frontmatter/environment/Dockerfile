FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        pyyaml==6.0.2

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design \
    && cd ant-design \
    && git checkout 7be2b3111741ecfa4bc00d9047080ca14f4bea77

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
