FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

# Sparse-checkout only the directories the task touches — keeps the image small.
RUN git clone --filter=blob:none --no-checkout https://github.com/ant-design/ant-design.git /workspace/ant-design \
    && cd /workspace/ant-design \
    && git sparse-checkout init --cone \
    && git sparse-checkout set components/affix components/config-provider \
    && git checkout 3980243572875b822d8df0b308980ad57afee284

WORKDIR /workspace/ant-design

RUN mkdir -p /logs/verifier
