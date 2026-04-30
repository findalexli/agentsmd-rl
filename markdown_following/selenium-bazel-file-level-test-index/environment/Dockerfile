FROM ruby:3.2.6-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        ca-certificates \
        patch \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN gem install --no-document rake:13.2.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git \
    && cd selenium \
    && git checkout 3334f0fd26025d51919292712bcda64a7edf5859

WORKDIR /workspace/selenium

RUN mkdir -p /logs/verifier
