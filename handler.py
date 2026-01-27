# handler.py - WORKING VERSION
import runpod
from llama_cpp import Llama
import os
import sys
import time

print("=" * 60)
print("🚀 LLaMA 3D Gift Ideas Generator")
print("=" * 60)

# Debug info
print(f"\n🐍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")

# Check for network volume
print("\n🔍 Checking for model file...")
possible_paths = [
    "/workspace/Llama-3.2-3B-Instruct-IQ3_M.gguf",
    "/model/Llama-3.2-3B-Instruct-IQ3_M.gguf",
    "/volume/Llama-3.2-3B-Instruct-IQ3_M.gguf",
]

model_path = None
for path in possible_paths:
    if os.path.exists(path):
        model_path = path
        print(f"✅ Model found at: {path}")
        size = os.path.getsize(path) / (1024**3)
        print(f"   Size: {size:.2f} GB")
        break

if not model_path:
    print("❌ Model not found in any location!")
    print("\n💡 Check endpoint configuration:")
    print("1. Go to Serverless → llama-3d-gifts → Manage")
    print("2. Verify Network Volume is attached")
    print("3. Check Mount Path matches one of the above")
    print("\n📋 Root directory (/):")
    for item in sorted(os.listdir('/')):
        if os.path.isdir(os.path.join('/', item)):
            print(f"  📁 {item}/")
    sys.exit(1)

# Load model
print(f"\n🔧 Loading model from: {model_path}")
print("This may take 30-60 seconds on CPU...")

try:
    llm = Llama(
        model_path=model_path,
        n_ctx=1024,      # Context size
        n_threads=4,     # CPU threads
        n_gpu_layers=0,  # CPU only
        verbose=True     # Show loading progress
    )
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def handler(job):
    """Main handler function - REQUIRED for RunPod"""
    print(f"\n🎯 Received job: {job.get('id', 'unknown')}")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        print(f"📝 Processing: {fun_fact}")
        
        prompt = f"""Generate 2-3 creative 3D printable gift ideas for someone who: {fun_fact}

For each idea provide:
• Name
• Brief description  
• Why it's suitable for 3D printing

Keep responses practical and concise."""

        print("🤖 Generating ideas...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=300,
            temperature=0.7,
            top_p=0.9,
            echo=False
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation took: {generation_time:.2f} seconds")
        
        result = response['choices'][0]['text'].strip()
        
        return {
            "status": "success",
            "ideas": result,
            "input": fun_fact,
            "generation_time": f"{generation_time:.2f}s",
            "model": "Llama-3.2-3B-Instruct"
        }
        
    except Exception as e:
        print(f"❌ Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# CRITICAL: Start the RunPod server
print("\n🏁 Starting RunPod serverless handler...")
print("Server is ready to accept requests!")
runpod.serverless.start({"handler": handler})