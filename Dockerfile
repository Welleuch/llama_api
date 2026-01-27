# Dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN pip install llama-cpp-python --no-cache-dir
RUN pip install runpod

# Copy handler
COPY handler.py /handler.py

# Run handler
CMD ["python", "-u", "/handler.py"]