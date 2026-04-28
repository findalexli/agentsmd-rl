FROM node:22-slim

RUN npm install -g pnpm@10.17.1 && \
    npm install -g tsx@4.21.0 && \
    apt-get update && apt-get install -y git python3 python3-pip --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED && \
    pip3 install pytest==8.3.4

WORKDIR /workspace/effect

RUN git clone --filter=blob:none https://github.com/Effect-TS/effect.git /workspace/effect && \
    git checkout 4f2107548fa64c21a8643b7b0efcd556cd16d4b9

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
