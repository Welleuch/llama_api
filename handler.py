# handler.py - FIXED VERSION
import runpod
import os
import sys
import time

print("=" * 50)
print("🚀 STARTING LLaMA CPU HANDLER")
print("=" * 50)

# Print Python info for debugging
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Check model path early
MODEL_PATH = "/model/Llama-3.2-3B-Instruct-IQ3_M.gguf"
print(f"\n📦 Model path: {MODEL_PATH}")
print(f"📂 Model exists: {os.path.exists(MODEL_PATH)}")

# List /model contents
if os.path.exists("/model"):
    print("\n📋 Contents of /model:")
    for item in os.listdir("/model"):
        full_path = os.path.join("/model", item)
        if os.path.isfile(full_path):
            size = os.path.getsize(full_path)
            print(f"  - {item} ({size / (1024**3):.2f} GB)")
else:
    print("\n❌ /model directory not found!")

# Try to import llama_cpp with fallback
try:
    from llama_cpp import Llama
    print("\n✅ llama_cpp imported successfully")
except ImportError as e:
    print(f"\n❌ Failed to import llama_cpp: {e}")
    print("Attempting to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
    from llama_cpp import Llama

# Global model instance
llm = None

def init_model():
    """Initialize model"""
    global llm
    try:
        print("\n🔧 Loading model...")
        
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,  # Small context for testing
            n_threads=2,
            n_gpu_layers=0,
            verbose=True
        )
        
        print("✅ Model loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def handler(job):
    """Main handler - MUST RETURN A DICT"""
    print(f"\n🎯 Received job: {job}")
    
    try:
        input_data = job.get("input", {})
        fun_fact = input_data.get("fun_fact", "test fact")
        
        print(f"📝 Processing: {fun_fact}")
        
        if llm is None:
            return {"status": "error", "message": "Model not loaded"}
        
        # Simple test prompt
        prompt = f"Suggest a gift for someone who: {fun_fact}"
        print(f"🤖 Generating with prompt: {prompt[:50]}...")
        
        response = llm(prompt, max_tokens=50, temperature=0.7)
        result = response['choices'][0]['text'].strip()
        
        return {
            "status": "success",
            "result": result,
            "input": fun_fact
        }
        
    except Exception as e:
        print(f"❌ Handler error: {e}")
        return {"status": "error", "message": str(e)}

# Main execution
print("\n🔄 Initializing...")
if init_model():
    print("\n🏁 Starting RunPod serverless handler...")
    # CRITICAL: This must be the last line - it keeps the process alive
    runpod.serverless.start({"handler": handler})
else:
    print("\n💥 Initialization failed. Container will exit.")
    # Don't exit - keep container alive for debugging
    print("⚠️ Keeping container alive for 300 seconds for debugging...")
    time.sleep(300)