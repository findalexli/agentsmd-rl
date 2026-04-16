FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the selenium repository at the base commit
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 5d23d81b3f04954eca5a6319ba2ac5a15cc05a33

# Install minimal dependencies for testing
WORKDIR /workspace/selenium/py
RUN pip install --no-cache-dir pytest rich filetype

# Create placeholder binary files so path resolution tests pass
RUN mkdir -p /workspace/selenium/py/selenium/webdriver/common/linux \
    && mkdir -p /workspace/selenium/py/selenium/webdriver/common/macos \
    && mkdir -p /workspace/selenium/py/selenium/webdriver/common/windows \
    && touch /workspace/selenium/py/selenium/webdriver/common/linux/selenium-manager \
    && touch /workspace/selenium/py/selenium/webdriver/common/macos/selenium-manager \
    && touch /workspace/selenium/py/selenium/webdriver/common/windows/selenium-manager.exe

# Make selenium package importable
ENV PYTHONPATH="/workspace/selenium/py"

WORKDIR /workspace/selenium
