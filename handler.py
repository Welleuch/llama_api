# handler.py - FINAL WORKING VERSION
import runpod
import os
import sys
import time

print("=" * 60)
print("🚀 LLaMA 3D Gift Ideas Generator - STARTING")
print("=" * 60)

# First, check if we can import llama_cpp
try:
    from llama_cpp import Llama
    print("✅ llama_cpp imported successfully")
except ImportError as e:
    print(f"❌ Failed to import llama_cpp: {e}")
    print("Installing llama-cpp-python...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
    from llama_cpp import Llama

# Find the model file
MODEL_NAME = "Llama-3.2-3B-Instruct-IQ3_M.gguf"
possible_paths = [
    "/model/" + MODEL_NAME,      # Most likely
    "/workspace/" + MODEL_NAME,  # Default
    "/volume/" + MODEL_NAME,     # Alternative
]

model_path = None
for path in possible_paths:
    if os.path.exists(path):
        model_path = path
        print(f"✅ Model found at: {path}")
        size_gb = os.path.getsize(path) / (1024**3)
        print(f"   Size: {size_gb:.2f} GB")
        break

if not model_path:
    print("❌ Model file not found!")
    print("Checking what's available:")
    
    # List all directories that might contain the model
    check_dirs = ['/', '/model', '/workspace', '/volume', '/data']
    for dir_path in check_dirs:
        if os.path.exists(dir_path):
            try:
                items = os.listdir(dir_path)
                print(f"📁 {dir_path}: {items}")
                
                # Look for any GGUF files
                gguf_files = [f for f in items if f.endswith('.gguf')]
                if gguf_files:
                    print(f"   Found GGUF files: {gguf_files}")
                    # Use the first GGUF file found
                    model_path = os.path.join(dir_path, gguf_files[0])
                    print(f"   Will use: {model_path}")
                    break
            except:
                print(f"📁 {dir_path}: (cannot list)")
    
    if not model_path:
        print("💡 No GGUF files found anywhere!")
        # Fallback to test mode
        print("💡 Running in TEST MODE (no model)")

# Load the model (if found)
llm = None
if model_path:
    try:
        print(f"\n🔧 Loading model from: {model_path}")
        print("This may take 30-60 seconds on CPU...")
        
        llm = Llama(
            model_path=model_path,
            n_ctx=512,      # Context size
            n_threads=4,    # CPU threads
            n_gpu_layers=0, # CPU only
            verbose=True    # Show loading progress
        )
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        print("💡 Will run in test mode")
else:
    print("💡 No model available - running in test mode")

# Handler function
def handler(job):
    print(f"\n🎯 Received job")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        
        print(f"📝 Fun fact: {fun_fact}")
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        # If model is loaded, use it
        if llm:
            prompt = f"""Generate 2 creative 3D printable gift ideas for someone who: {fun_fact}

For each idea provide:
1. Name
2. Brief description
3. Why it's suitable for 3D printing

Keep responses practical and concise."""

            print("🤖 Generating ideas with LLaMA...")
            response = llm(prompt, max_tokens=250, temperature=0.7)
            
            result = response['choices'][0]['text'].strip()
            
            return {
                "status": "success",
                "ideas": result,
                "input": fun_fact,
                "model": "Llama-3.2-3B-Instruct"
            }
        else:
            # Test mode - no model loaded
            return {
                "status": "test_mode",
                "message": "Model not loaded - running in test mode",
                "suggestion": f"For '{fun_fact}', consider: 3D printed plant markers with constellation designs",
                "note": "Check logs for model loading issues"
            }
        
    except Exception as e:
        print(f"❌ Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Start the server
print("\n🏁 Starting RunPod server...")
if llm:
    print("✅ Ready to generate 3D gift ideas!")
else:
    print("⚠️  Running in TEST MODE - check model configuration")

runpod.serverless.start({"handler": handler})