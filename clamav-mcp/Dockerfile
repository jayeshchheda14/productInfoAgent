FROM python:3.11-slim

# Install ClamAV
RUN apt-get update && \
    apt-get install -y clamav clamav-daemon && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Update virus definitions
RUN freshclam

# Install MCP dependencies
RUN pip install --no-cache-dir mcp

# Create app directory
WORKDIR /app
COPY clamav_mcp_server.py .

# Keep container running
CMD ["tail", "-f", "/dev/null"]
