# handler.py - DUAL MODEL VERSION (CORRECTED PATHS)
import runpod
from llama_cpp import Llama
import os
import sys
import time

print("=" * 60)
print("🚀 DUAL MODEL 3D Gift Ideas Generator")
print("Model 1: Llama-3.2-3B-Instruct")
print("Model 2: Qwen2.5-1.5B-Instruct")
print("=" * 60)

# CORRECTED PATHS - BOTH IN /runpod-volume/
LLAMA_MODEL_PATH = "/runpod-volume/Llama-3.2-3B-Instruct-IQ3_M.gguf"
QWEN_MODEL_PATH = "/runpod-volume/qwen2.5-1.5b-instruct-q4_k_m.gguf"

print(f"📦 Llama model: {LLAMA_MODEL_PATH}")
print(f"📦 Qwen model: {QWEN_MODEL_PATH}")

# Load models
models = {}
model_loaded = False

def load_model(model_path, model_name):
    """Load a single model"""
    if os.path.exists(model_path):
        size_gb = os.path.getsize(model_path) / (1024**3)
        print(f"\n🔧 Loading {model_name} ({size_gb:.2f} GB)...")
        
        try:
            llm = Llama(
                model_path=model_path,
                n_ctx=1024,      # Context size
                n_threads=4,     # Use 4 CPU threads
                n_gpu_layers=0,  # CPU only
                verbose=True     # Show loading progress
            )
            print(f"✅ {model_name} loaded successfully!")
            
            # Quick test
            test_response = llm("Hello", max_tokens=5)
            print(f"🧪 Test: '{test_response['choices'][0]['text']}'")
            
            return llm
        except Exception as e:
            print(f"❌ {model_name} loading failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        print(f"❌ {model_name} file not found at: {model_path}")
        # Debug: list files in /runpod-volume/
        try:
            print(f"🔍 Listing /runpod-volume/ contents:")
            for item in os.listdir("/runpod-volume/"):
                if item.endswith(".gguf"):
                    size = os.path.getsize(f"/runpod-volume/{item}") / (1024**3)
                    print(f"   - {item} ({size:.2f} GB)")
        except Exception as list_err:
            print(f"   Could not list directory: {list_err}")
        return None

# Load both models
print("\n" + "="*40)
print("Loading models...")
print("="*40)

llama_llm = load_model(LLAMA_MODEL_PATH, "Llama-3.2-3B-Instruct")
qwen_llm = load_model(QWEN_MODEL_PATH, "Qwen2.5-1.5B-Instruct")

# Check which models are available
models_available = []
if llama_llm:
    models["llama"] = llama_llm
    models_available.append("llama")
if qwen_llm:
    models["qwen"] = qwen_llm
    models_available.append("qwen")

if models_available:
    model_loaded = True
    print(f"\n✅ Ready with models: {', '.join(models_available)}")
else:
    print("\n❌ No models loaded!")
    model_loaded = False

def generate_with_model(llm, prompt, model_name):
    """Generate response with a specific model"""
    print(f"🤖 Generating with {model_name}...")
    start_time = time.time()
    
    response = llm(
        prompt,
        max_tokens=400,      # Slightly less for dual output
        temperature=0.7,     # Creative but focused
        top_p=0.9,           # Nucleus sampling
        echo=False
    )
    
    generation_time = time.time() - start_time
    result = response['choices'][0]['text'].strip()
    
    print(f"⏱️ {model_name}: {generation_time:.2f}s, {len(result.split())} words")
    return result, generation_time

def handler(job):
    """Main handler function"""
    print(f"\n🎯 Received job")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        model_choice = input_data.get("model", "both").lower()  # "llama", "qwen", or "both"
        
        print(f"📝 Input: {fun_fact}")
        print(f"🤖 Model choice: {model_choice}")
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        if not model_loaded:
            return {
                "status": "error",
                "message": "No models loaded",
                "available": models_available
            }
        
        # Create prompt for 3D gift ideas
        prompt = f"""You are a creative 3D printing expert. Based on this information about the gift receiver: "{fun_fact}"

Generate 2 unique 3D printable gift ideas. For each idea provide:
1. **Name**: Creative name for the item
2. **Description**: Brief description of what it is
3. **Why it fits**: Why this is suitable for the person
4. **Difficulty**: Printing difficulty (Beginner/Intermediate/Advanced)

Format each idea clearly with bullet points.

Now generate ideas for: "{fun_fact}"
"""
        
        results = {}
        
        # Generate based on model choice
        if model_choice == "both" or model_choice == "llama":
            if "llama" in models:
                llama_result, llama_time = generate_with_model(
                    models["llama"], prompt, "Llama 3.2 3B"
                )
                results["llama"] = {
                    "ideas": llama_result,
                    "generation_time": f"{llama_time:.2f}s",
                    "model": "Llama-3.2-3B-Instruct"
                }
        
        if model_choice == "both" or model_choice == "qwen":
            if "qwen" in models:
                qwen_result, qwen_time = generate_with_model(
                    models["qwen"], prompt, "Qwen2.5 1.5B"
                )
                results["qwen"] = {
                    "ideas": qwen_result,
                    "generation_time": f"{qwen_time:.2f}s",
                    "model": "Qwen2.5-1.5B-Instruct"
                }
        
        if not results:
            return {
                "status": "error",
                "message": f"Requested model '{model_choice}' not available",
                "available": list(models.keys())
            }
        
        response = {
            "status": "success",
            "original_fact": fun_fact,
            "models_available": models_available
        }
        
        if model_choice == "both":
            response["both_models"] = results
        elif model_choice == "llama" and "llama" in results:
            response.update(results["llama"])
        elif model_choice == "qwen" and "qwen" in results:
            response.update(results["qwen"])
        
        return response
        
    except Exception as e:
        print(f"❌ Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "type": type(e).__name__}

print("\n🏁 Starting RunPod serverless handler...")
print(f"Available models: {models_available}")
print("Ready to generate 3D gift ideas! 🎁")
print("\n📝 Usage:")
print("  - To use Llama only: {\"fun_fact\": \"loves cats\", \"model\": \"llama\"}")
print("  - To use Qwen only: {\"fun_fact\": \"loves cats\", \"model\": \"qwen\"}")
print("  - To use both: {\"fun_fact\": \"loves cats\", \"model\": \"both\"}")
print("  - Default (both): {\"fun_fact\": \"loves cats\"}")

runpod.serverless.start({"handler": handler})