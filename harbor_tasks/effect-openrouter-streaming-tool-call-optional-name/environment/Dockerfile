FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.17.1

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/Effect-TS/effect.git effect \
    && cd effect \
    && git checkout 4f2107548fa64c21a8643b7b0efcd556cd16d4b9

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier

CMD ["bash"]
