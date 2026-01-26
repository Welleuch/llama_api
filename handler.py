# handler.py
import runpod
import os
import sys
import time

print("🚀 Starting handler...")
print(f"Python version: {sys.version}")

try:
    from llama_cpp import Llama
    print("✅ llama-cpp-python imported successfully")
except ImportError as e:
    print(f"❌ Failed to import llama_cpp: {e}")
    print("Trying to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
    from llama_cpp import Llama

# Model path - mounted from network volume
MODEL_PATH = "/model/Llama-3.2-3B-Instruct-IQ3_M.gguf"

# Global model instance
llm = None

def init_model():
    """Initialize the model once when container starts"""
    global llm
    
    print(f"📂 Checking model path: {MODEL_PATH}")
    print(f"📦 Model exists: {os.path.exists(MODEL_PATH)}")
    
    # Debug: List files in /model
    if os.path.exists("/model"):
        print("📋 Contents of /model:")
        for item in os.listdir("/model"):
            item_path = os.path.join("/model", item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"  - {item} ({size / (1024**3):.2f} GB)")
            else:
                print(f"  - {item}/ (directory)")
    else:
        print("❌ /model directory does not exist!")
        return False
    
    try:
        print("🔧 Loading model...")
        start_time = time.time()
        
        # Load model with optimized settings
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=-1,  # Use all GPU layers
            verbose=True  # Enable verbose for debugging
        )
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Test inference
        test_prompt = "Hello"
        test_output = llm(test_prompt, max_tokens=10, temperature=0)
        print(f"🧪 Test inference successful: '{test_output['choices'][0]['text']}'")
        
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
        
        # Simplified prompt for testing
        prompt = f"""Generate 3 creative 3D printable gift ideas for someone who: {fun_fact}

For each idea, provide:
1. Name
2. Brief description
3. Why it's suitable

Keep responses concise."""
        
        print("🤖 Generating ideas...")
        start_time = time.time()
        
        # Generate response
        response = llm(
            prompt,
            max_tokens=300,
            temperature=0.7,
            echo=False
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation took {generation_time:.2f} seconds")
        
        result_text = response['choices'][0]['text'].strip()
        
        return {
            "status": "success",
            "ideas": result_text,
            "original_fact": fun_fact,
            "generation_time": f"{generation_time:.2f}s"
        }
        
    except Exception as e:
        print(f"❌ Error in handler: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": str(e)
        }

# Initialize model
print("🔄 Initializing model...")
if init_model():
    print("🏁 Model initialized successfully. Starting RunPod server...")
    runpod.serverless.start({"handler": generate_3d_idea})
else:
    print("💥 Failed to initialize model. Exiting...")