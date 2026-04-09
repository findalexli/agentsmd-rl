FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-wget curl git ca-certificates build-essential tmux \
        libicu-dev libssl3 && \
    rm -rf /var/lib/apt/lists/*

# Install PowerShell for running/validating PowerShell scripts
# Install from Microsoft repository
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget apt-transport-https software-properties-common && \
    wget -q "https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb" -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends powershell && \
    rm -rf /var/lib/apt/lists/*

# dotnet/maui is very large — use shallow snapshot
RUN git init /workspace/maui && \
    cd /workspace/maui && \
    git remote add origin https://github.com/dotnet/maui.git && \
    git fetch --depth=1 origin 62894e405b36c5b6cede44fdfe56832e26cdc8af && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# No special deps needed — tests use subprocess to validate PowerShell
RUN mkdir -p /logs/verifier
