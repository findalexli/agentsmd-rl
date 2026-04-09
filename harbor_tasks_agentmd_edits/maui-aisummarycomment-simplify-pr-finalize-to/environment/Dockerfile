FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install dependencies including PowerShell
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        wget apt-transport-https software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Install PowerShell (pwsh) for PowerShell script testing
RUN wget -q "https://packages.microsoft.com/config/debian/$(. /etc/os-release && echo $VERSION_ID)/packages-microsoft-prod.deb" -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends powershell && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git checkout f6bafa6e590e1d1dba4b2df2e4dc20a6bad67b7a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
