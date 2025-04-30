# Build stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies needed for downloads
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Create directories for tools
WORKDIR /tools

# Download and prepare tools
RUN curl -fsSL https://releases.hashicorp.com/terraform/1.11.3/terraform_1.11.3_linux_amd64.zip -o terraform.zip \
    && unzip terraform.zip \
    && rm terraform.zip \
    \
    && curl -fsSL https://golang.org/dl/go1.24.0.linux-amd64.tar.gz -o go.tar.gz \
    && tar -xzf go.tar.gz \
    && rm go.tar.gz \
    \
    && curl -fsSL https://get.helm.sh/helm-v3.17.0-linux-amd64.tar.gz -o helm.tar.gz \
    && tar -xzf helm.tar.gz \
    && mv linux-amd64/helm /tools/ \
    && rm -rf helm.tar.gz linux-amd64 \
    \
    && curl -fsSL https://dl.k8s.io/release/v1.32.3/bin/linux/amd64/kubectl -o kubectl \
    && chmod +x kubectl \
    \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up workspace
WORKDIR /workspace

# Copy requirements file
COPY requirements.txt /workspace/

# Set PATH for Go
ENV PATH="/usr/local/go/bin:$PATH"

# Default command
CMD ["/bin/bash"]
