FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install llama-cpp-python --no-cache-dir
RUN pip install runpod

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]