FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 26bb358ea971aebe30729f8a7ae4f3f0fedb1d5a

RUN pip install --no-cache-dir \
    torch==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu

RUN cd /workspace/transformers && pip install --no-cache-dir -e .

RUN pip install --no-cache-dir pytest==8.3.4 ruff==0.11.0

RUN mkdir -p /logs/verifier
