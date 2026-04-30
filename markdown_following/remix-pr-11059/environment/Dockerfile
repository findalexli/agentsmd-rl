FROM node:24-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    fonts-liberation \
    git \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libu2f-udev \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    python3 \
    python3-pip \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.26.0

WORKDIR /workspace/remix

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix \
    && git checkout aec113e9563f860ea1d0abfcbd2743dd2f6c6bc5

ENV CI=true
RUN pnpm install

RUN pnpm --filter @remix-run/component exec npx playwright install chromium

RUN python3 -m pip install pytest==8.3.4 --break-system-packages --quiet

RUN mkdir -p /logs/verifier
