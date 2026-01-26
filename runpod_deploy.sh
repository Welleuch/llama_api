#!/bin/bash
# runpod_deploy.sh

echo "🚀 Building Docker image..."
docker build -t yourusername/llama-3d-ideas:latest .

echo "📦 Pushing to Docker Hub..."
docker push yourusername/llama-3d-ideas:latest

echo "✅ Ready to deploy on RunPod!"