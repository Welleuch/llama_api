# handler.py - UPDATED WITH /workspace
import runpod
from llama_cpp import Llama
import os
import sys

print("=" * 50)
print("🚀 LLaMA 3D Ideas Generator")
print("=" * 50)

# FIX: Network volumes mount to /workspace by default
MODEL_PATH = "/workspace/Llama-3.2-3B-Instruct-IQ3_M.gguf"
print(f"📦 Model path: {MODEL_PATH}")

# Debug: Check what's in /workspace
print("\n📋 Checking /workspace directory...")
if os.path.exists("/workspace"):
    print("✅ /workspace exists!")
    items = os.listdir("/workspace")
    if items:
        print("Contents:")
        for item in items:
            full_path = os.path.join("/workspace", item)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                print(f"  📄 {item} ({size / (1024**3):.2f} GB)")
            else:
                print(f"  📁 {item}/")
    else:
        print("  (empty)")
else:
    print("❌ /workspace does not exist!")

if not os.path.exists(MODEL_PATH):
    print(f"\n❌ ERROR: Model not found at {MODEL_PATH}")
    
    # Also check /model in case it was manually configured
    if os.path.exists("/model"):
        print("⚠️  Found /model directory. Checking...")
        for item in os.listdir("/model"):
            print(f"  - {item}")
        MODEL_PATH = "/model/Llama-3.2-3B-Instruct-IQ3_M.gguf"
        print(f"Trying path: {MODEL_PATH}")
    
    if not os.path.exists(MODEL_PATH):
        print("\n💡 Fix: Check network volume mount path in endpoint config")
        print("Default is /workspace, but might be configured differently")
        sys.exit(1)

print(f"\n✅ Model found! Size: {os.path.getsize(MODEL_PATH) / (1024**3):.2f} GB")

# Load model
print("\n🔧 Loading model (CPU only)...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=1024,
    n_threads=4,
    n_gpu_layers=0,
    verbose=True
)

print("✅ Model loaded successfully!")

def handler(job):
    """Main handler function"""
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "")
        
        print(f"\n🎯 Processing: {fun_fact}")
        
        prompt = f"""Suggest 3 creative 3D printable gift ideas for someone who: {fun_fact}

For each idea, provide:
1. Name
2. Brief description
3. Why it's suitable

Keep responses concise and practical for 3D printing."""

        response = llm(prompt, max_tokens=300, temperature=0.7)
        result = response['choices'][0]['text'].strip()
        
        return {
            "status": "success",
            "ideas": result,
            "input": fun_fact,
            "model": "Llama-3.2-3B-Instruct (CPU)"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

print("\n🏁 Starting RunPod serverless handler...")
runpod.serverless.start({"handler": handler})