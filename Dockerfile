# Dockerfile - CPU ONLY
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN pip install llama-cpp-python --no-cache-dir
RUN pip install runpod

# Copy files
WORKDIR /app
COPY handler.py .
COPY requirements.txt .

CMD ["python", "-u", "handler.py"]