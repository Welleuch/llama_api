# handler.py - FINAL WORKING VERSION
import runpod
from llama_cpp import Llama
import os
import sys
import time

print("=" * 60)
print("🚀 LLaMA 3D Gift Ideas Generator")
print("=" * 60)

# CORRECT PATH - based on debug results
MODEL_PATH = "/runpod-volume/Llama-3.2-3B-Instruct-IQ3_M.gguf"

print(f"📦 Model path: {MODEL_PATH}")
print(f"✅ File exists: {os.path.exists(MODEL_PATH)}")

if os.path.exists(MODEL_PATH):
    size_gb = os.path.getsize(MODEL_PATH) / (1024**3)
    print(f"📏 Size: {size_gb:.2f} GB")
    
    # Load the model
    print("\n🔧 Loading model...")
    print("This may take 30-60 seconds on CPU...")
    
    try:
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=1024,      # Context size
            n_threads=4,     # Use 4 CPU threads
            n_gpu_layers=0,  # CPU only
            verbose=True     # Show loading progress
        )
        print("✅ Model loaded successfully!")
        model_loaded = True
        
        # Quick test
        test_response = llm("Hello", max_tokens=5)
        print(f"🧪 Test response: '{test_response['choices'][0]['text']}'")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        model_loaded = False
else:
    print("❌ Model file not found!")
    model_loaded = False

def handler(job):
    """Main handler function"""
    print(f"\n🎯 Received job")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        
        print(f"📝 Processing: {fun_fact}")
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        if not model_loaded:
            return {
                "status": "error",
                "message": "Model not loaded",
                "debug": f"Path: {MODEL_PATH}, Exists: {os.path.exists(MODEL_PATH)}"
            }
        
        # Create prompt for 3D gift ideas
        prompt = f"""You are a creative 3D printing expert. Based on this information about the gift receiver: "{fun_fact}"

Generate 3 unique 3D printable gift ideas. For each idea provide:
1. **Name**: Creative name for the item
2. **Description**: Brief description of what it is
3. **Why it fits**: Why this is suitable for the person
4. **Difficulty**: Printing difficulty (Beginner/Intermediate/Advanced)

Format each idea clearly with bullet points.

Examples:
- For "loves cats and surfing", suggest "Surfing Cat Statuette"
- For "gardener and astronomer", suggest "Planetary Plant Marker Set"

Now generate ideas for: "{fun_fact}"
"""
        
        print("🤖 Generating ideas...")
        start_time = time.time()
        
        # Generate response
        response = llm(
            prompt,
            max_tokens=500,      # Enough for 3 ideas
            temperature=0.7,     # Creative but focused
            top_p=0.9,           # Nucleus sampling
            echo=False
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation took: {generation_time:.2f} seconds")
        
        result = response['choices'][0]['text'].strip()
        
        print(f"✅ Generated {len(result.split())} words")
        
        return {
            "status": "success",
            "ideas": result,
            "original_fact": fun_fact,
            "generation_time": f"{generation_time:.2f}s",
            "model": "Llama-3.2-3B-Instruct"
        }
        
    except Exception as e:
        print(f"❌ Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "type": type(e).__name__}

print("\n🏁 Starting RunPod serverless handler...")
print("Ready to generate 3D gift ideas! 🎁")
runpod.serverless.start({"handler": handler})