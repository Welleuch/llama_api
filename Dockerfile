# Dockerfile - Simplified version
FROM runpod/base:0.4.0-cuda11.8.0

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --no-cache-dir
RUN pip install runpod

# Copy handler
COPY handler.py /handler.py
COPY requirements.txt /requirements.txt

# Run handler
CMD ["python", "-u", "/handler.py"]