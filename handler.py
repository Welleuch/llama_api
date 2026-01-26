# handler.py
import runpod
from llama_cpp import Llama
import os
import time

print("🚀 Starting CPU LLaMA handler...")

# Model path - mounted from network volume
MODEL_PATH = "/model/Llama-3.2-3B-Instruct-IQ3_M.gguf"

# Global model instance
llm = None

def init_model():
    """Initialize the model once when container starts"""
    global llm
    
    print(f"📂 Checking model path: {MODEL_PATH}")
    print(f"📦 Model exists: {os.path.exists(MODEL_PATH)}")
    
    # Debug: Check /model contents
    if os.path.exists("/model"):
        model_files = [f for f in os.listdir("/model") if f.endswith('.gguf')]
        print(f"📋 Found GGUF files: {model_files}")
        
        # List all files for debugging
        print("All files in /model:")
        for item in os.listdir("/model"):
            path = os.path.join("/model", item)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                print(f"  - {item} ({size / (1024**3):.2f} GB)")
    else:
        print("❌ /model directory does not exist!")
        return False
    
    try:
        print("🔧 Loading model (CPU only)...")
        start_time = time.time()
        
        # CPU-only settings (n_gpu_layers=0)
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=1024,  # Reduced for CPU memory
            n_threads=4,  # Number of CPU threads
            n_gpu_layers=0,  # CPU ONLY
            n_batch=512,  # Batch size for processing
            verbose=True  # Show loading progress
        )
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Quick test
        test_response = llm("Hello", max_tokens=5, temperature=0)
        print(f"🧪 Test response: '{test_response['choices'][0]['text']}'")
        
        # Show model info
        print(f"📊 Model context size: {llm.n_ctx()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_3d_idea(job):
    """Main handler function for RunPod"""
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "")
        
        print(f"🎯 Received request: {fun_fact}")
        
        if llm is None:
            return {
                "status": "error",
                "message": "Model not loaded. Please wait for initialization."
            }
        
        # Optimized prompt for faster CPU generation
        prompt = f"""Generate 2 creative 3D printable gift ideas for someone who: {fun_fact}

For each idea, provide:
1. Name
2. Brief description (1-2 sentences)
3. Why it's suitable

Keep responses short and practical for 3D printing."""

        print("🤖 Generating ideas (CPU)...")
        start_time = time.time()
        
        # Generate with conservative settings for CPU
        response = llm(
            prompt,
            max_tokens=250,  # Shorter for faster response
            temperature=0.7,
            top_p=0.9,
            echo=False
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation took {generation_time:.2f} seconds")
        
        result_text = response['choices'][0]['text'].strip()
        
        return {
            "status": "success",
            "ideas": result_text,
            "original_fact": fun_fact,
            "generation_time": f"{generation_time:.2f}s",
            "model": "Llama-3.2-3B-Instruct-IQ3_M (CPU)",
            "note": "Running on CPU - responses may be slower"
        }
        
    except Exception as e:
        print(f"❌ Error in handler: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }

# Initialize model
print("🔄 Initializing model (this may take 30-60 seconds)...")
if init_model():
    print("🏁 Model initialized successfully. Starting RunPod server...")
    runpod.serverless.start({"handler": generate_3d_idea})
else:
    print("💥 Failed to initialize model. Exiting...")