FROM python:3.12-slim

RUN pip install pytest==8.3.4

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/inclusionAI/AReaL.git areal \
    && cd areal && git checkout dbc49386907b05222af70cc19a3b1dbf434e1c32

RUN mkdir -p /logs/verifier
