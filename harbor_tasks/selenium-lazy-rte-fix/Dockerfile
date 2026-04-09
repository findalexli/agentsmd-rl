FROM openjdk:21-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pytest pyyaml --quiet

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium

WORKDIR /workspace/selenium
RUN git checkout 4bb23f484eec6f986b563fb3146cb64dcbcc0187

RUN mkdir -p /logs/verifier
