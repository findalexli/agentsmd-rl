FROM node:22-slim

RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN npm install -g tsx@4.19.2

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix

WORKDIR /workspace/remix

RUN git checkout 3aa3d939d558aac03bfb0f3796bb7d6d4aacfa70

RUN corepack enable pnpm && corepack prepare pnpm@10.26.0 --activate

RUN pnpm install --frozen-lockfile

RUN mkdir -p /tests /logs/verifier
