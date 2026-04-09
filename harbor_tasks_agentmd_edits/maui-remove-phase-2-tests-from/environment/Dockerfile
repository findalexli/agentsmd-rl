FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux \
        libicu-dev wget apt-transport-https software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Install PowerShell (pwsh) for testing PowerShell scripts
RUN wget -q "https://packages.microsoft.com/config/debian/$(. /etc/os-release && echo $VERSION_ID)/packages-microsoft-prod.deb" -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends powershell && \
    rm -rf /var/lib/apt/lists/*

# dotnet/maui is huge — shallow snapshot of base commit only
RUN git init /workspace/maui && \
    cd /workspace/maui && \
    git remote add origin https://github.com/dotnet/maui.git && \
    git fetch --depth=1 origin d417bea8d060b23aed36aa2e5f4a2bda2eb84a88 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# No additional deps needed — tests only read file contents and run PowerShell syntax checks
RUN mkdir -p /logs/verifier
