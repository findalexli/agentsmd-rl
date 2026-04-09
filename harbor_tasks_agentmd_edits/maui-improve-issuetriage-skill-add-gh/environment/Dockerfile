FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl git ca-certificates build-essential tmux \
        libicu-dev wget && \
    rm -rf /var/lib/apt/lists/*

# Install PowerShell for running/validating PowerShell scripts
# Download directly since the Microsoft repo method does not work on Trixie
RUN curl -L -o /tmp/powershell.tar.gz "https://github.com/PowerShell/PowerShell/releases/download/v7.4.2/powershell-7.4.2-linux-x64.tar.gz" && \
    mkdir -p /opt/microsoft/powershell/7 && \
    tar zxf /tmp/powershell.tar.gz -C /opt/microsoft/powershell/7 && \
    rm /tmp/powershell.tar.gz && \
    chmod +x /opt/microsoft/powershell/7/pwsh && \
    ln -s /opt/microsoft/powershell/7/pwsh /usr/bin/pwsh

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
