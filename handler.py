# handler.py
import runpod
from llama_cpp import Llama
import os
import time

# Model path - mounted from network volume
MODEL_PATH = "/model/Llama-3.2-3B-Instruct-IQ3_M.gguf"

# Global model instance
llm = None
print("🚀 Starting handler initialization...")

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
            size = os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            print(f"  - {item} ({size / (1024**3):.2f} GB)")
    else:
        print("❌ /model directory does not exist!")
    
    try:
        print("🔧 Loading model...")
        start_time = time.time()
        
        # Load model with optimized settings
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,  # Context length (adjust as needed)
            n_threads=4,  # CPU threads
            n_gpu_layers=-1,  # Use all GPU layers (-1 = all)
            verbose=False
        )
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Test inference
        test_prompt = "Hello"
        test_output = llm(test_prompt, max_tokens=10, temperature=0)
        print(f"🧪 Test inference: {test_output['choices'][0]['text'][:50]}...")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()

def generate_3d_idea(job):
    """Main handler function for RunPod"""
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "")
        
        print(f"🎯 Received request: {fun_fact[:50]}...")
        
        # Enhanced prompt for 3D printing ideas
        prompt = f"""You are a creative 3D printing expert. Based on this information about the gift receiver: "{fun_fact}"

Generate 3 unique 3D printable gift ideas. For each idea provide:
1. **Name**: Creative name for the item
2. **Description**: Brief description of what it is
3. **Why it fits**: Why this is suitable for the person
4. **Difficulty**: Printing difficulty (Beginner/Intermediate/Advanced)
5. **Estimated print time**: Rough estimate in hours
6. **Material suggestions**: Recommended filament types

Format each idea clearly with headings and bullet points.

Examples:
- If input is "loves cats and surfing", suggest "Surfing Cat Statuette"
- If input is "gardener and astronomer", suggest "Planetary Plant Marker Set"

Now generate ideas for: "{fun_fact}"
"""

        print("🤖 Generating ideas...")
        start_time = time.time()
        
        # Generate response
        response = llm(
            prompt,
            max_tokens=800,
            temperature=0.7,
            top_p=0.9,
            stop=["\n\n", "###", "---"]
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation took {generation_time:.2f} seconds")
        
        result_text = response['choices'][0]['text'].strip()
        
        return {
            "status": "success",
            "ideas": result_text,
            "original_fact": fun_fact,
            "generation_time": f"{generation_time:.2f}s",
            "model": "Llama-3.2-3B-Instruct-IQ3_M"
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

# Initialize model when container starts
init_model()

# Start RunPod serverless handler
print("🏁 Handler ready. Starting RunPod server...")
runpod.serverless.start({"handler": generate_3d_idea})