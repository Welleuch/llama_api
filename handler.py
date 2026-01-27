# handler.py - FINAL VERSION
import runpod
from llama_cpp import Llama
import os
import sys
import time

print("=" * 60)
print("🚀 LLaMA 3D Gift Ideas Generator")
print("=" * 60)

# Dynamic model path detection
def find_model():
    """Find where the model is mounted"""
    # Possible mount locations
    possible_paths = [
        ("/workspace/Llama-3.2-3B-Instruct-IQ3_M.gguf", "Default RunPod"),
        ("/model/Llama-3.2-3B-Instruct-IQ3_M.gguf", "Custom mount"),
        ("/volume/Llama-3.2-3B-Instruct-IQ3_M.gguf", "Alternative"),
        ("/data/Llama-3.2-3B-Instruct-IQ3_M.gguf", "Data mount"),
    ]
    
    print("\n🔍 Looking for model file...")
    
    for path, description in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found at: {path} ({description})")
            size = os.path.getsize(path) / (1024**3)
            print(f"   Size: {size:.2f} GB")
            return path
        
        # Check if directory exists
        dir_path = os.path.dirname(path)
        if os.path.exists(dir_path):
            print(f"📁 Directory exists: {dir_path}")
            print(f"  Contents: {os.listdir(dir_path)}")
    
    # If not found, check root directories
    print("\n📋 Checking root directories:")
    for item in sorted(os.listdir('/')):
        if os.path.isdir(os.path.join('/', item)):
            print(f"  📁 {item}/")
            try:
                contents = os.listdir(os.path.join('/', item))
                if contents:
                    print(f"    Contents: {contents[:5]}{'...' if len(contents) > 5 else ''}")
            except:
                pass
    
    return None

# Find model
MODEL_PATH = find_model()

if not MODEL_PATH:
    print("\n❌ ERROR: Model file not found!")
    print("\n💡 SOLUTION:")
    print("1. Network volume MUST be attached during endpoint creation")
    print("2. Create NEW endpoint with volume ID: ak5dwgtyk9")
    print("3. Mount path should be: /workspace")
    print("4. Check that model file exists in the volume")
    
    # Keep container alive for debugging
    print("\n⏳ Container will stay alive for 5 minutes...")
    time.sleep(300)
    sys.exit(1)

print(f"\n✅ Using model: {MODEL_PATH}")

# Load model
print("\n🔧 Loading model (CPU only, this takes 30-60 seconds)...")
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=1024,
        n_threads=4,
        n_gpu_layers=0,
        verbose=True
    )
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    import traceback
    traceback.print_exc()
    time.sleep(300)
    sys.exit(1)

def handler(job):
    """Main handler function"""
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        
        if not fun_fact:
            return {"status": "error", "message": "Please provide a fun_fact"}
        
        print(f"\n🎯 Processing request: '{fun_fact}'")
        
        prompt = f"""Suggest 2-3 creative 3D printable gift ideas for someone who: {fun_fact}

For each idea, provide:
• Name
• Brief description
• Why it's suitable

Keep responses practical for 3D printing."""

        print("🤖 Generating ideas...")
        response = llm(prompt, max_tokens=250, temperature=0.7)
        result = response['choices'][0]['text'].strip()
        
        print("✅ Generation complete!")
        
        return {
            "status": "success",
            "ideas": result,
            "input": fun_fact,
            "model": "Llama-3.2-3B-Instruct"
        }
        
    except Exception as e:
        print(f"❌ Handler error: {e}")
        return {"status": "error", "message": str(e)}

print("\n🏁 Starting RunPod serverless handler...")
runpod.serverless.start({"handler": handler})