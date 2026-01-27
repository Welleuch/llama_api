# handler.py - FIXED VERSION WITH BETTER FORMAT HANDLING
import runpod
from llama_cpp import Llama
import os
import sys
import time
import re

print("=" * 60)
print("🚀 3D PRINTING GIFT IDEA GENERATOR")
print("Optimized for: Text → Image → 3D Model Pipeline")
print("Model: Qwen2.5-1.5B-Instruct")
print("=" * 60)

# MODEL PATH
MODEL_PATH = "/runpod-volume/qwen2.5-1.5b-instruct-q4_k_m.gguf"

print(f"📦 Model: {MODEL_PATH}")
print(f"✅ File exists: {os.path.exists(MODEL_PATH)}")

# Load the model
llm = None
if os.path.exists(MODEL_PATH):
    size_gb = os.path.getsize(MODEL_PATH) / (1024**3)
    print(f"📏 Size: {size_gb:.2f} GB")
    
    print("\n🔧 Loading model...")
    try:
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
            verbose=True
        )
        print("✅ Model loaded successfully!")
        
        # Quick test
        test_response = llm("Hello", max_tokens=10)
        print(f"🧪 Test OK")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        llm = None
else:
    print("❌ Model file not found!")

def generate_gift_idea(fun_fact, color="gray", material="PLA"):
    """Generate a 3D printable gift idea with DfAM constraints"""
    
    prompt = f"""You are a professional 3D printing designer. Create a gift for someone who: "{fun_fact}"

MATERIAL: {color} {material} filament
PRINTING: FDM (Fused Deposition Modeling)

CRITICAL PRINTING RULES:
• Minimal or no supports needed
• Avoid overhangs >45 degrees
• No separate parts - one solid object
• No tiny details <2mm
• Self-supporting design

FORMAT YOUR ANSWER EXACTLY LIKE THIS:

[IDEA NAME]
A creative name for your 3D printable gift

[PRINTABILITY]  
Beginner, Intermediate, or Advanced

[IMAGE DESCRIPTION]
A detailed description for AI image generation. Describe:
- The object from front view
- Shape, size, key features
- That it's a gray PLA 3D printable object
- Style: low-poly or clean 3D model
- Example: "A low-poly rocket ship coffee mug, viewed from front. Smooth gray PLA surface, geometric shapes, studio lighting"

NOW CREATE FOR: "{fun_fact}" using {color} {material}"""
    
    return prompt

def parse_response(text):
    """Parse the structured response from the model"""
    print("🔍 Parsing model response...")
    
    # Initialize with defaults
    result = {
        "name": "3D Printed Gift Idea",
        "printability": "Intermediate",
        "image_prompt": f"A 3D printable object for someone who loves {text.split('loves')[-1][:50] if 'loves' in text else 'this hobby'}, gray PLA material, low-poly style, front view"
    }
    
    # Try to extract [IDEA NAME]
    name_match = re.search(r'\[IDEA NAME\](.*?)(?=\[PRINTABILITY\]|\[IMAGE DESCRIPTION\]|$)', text, re.DOTALL | re.IGNORECASE)
    if name_match:
        result["name"] = name_match.group(1).strip()
        print(f"✅ Found name: {result['name']}")
    
    # Try to extract [PRINTABILITY]
    print_match = re.search(r'\[PRINTABILITY\](.*?)(?=\[IMAGE DESCRIPTION\]|$)', text, re.DOTALL | re.IGNORECASE)
    if print_match:
        result["printability"] = print_match.group(1).strip()
        print(f"✅ Found printability: {result['printability']}")
    
    # Try to extract [IMAGE DESCRIPTION]
    desc_match = re.search(r'\[IMAGE DESCRIPTION\](.*?)$', text, re.DOTALL | re.IGNORECASE)
    if desc_match:
        result["image_prompt"] = desc_match.group(1).strip()
        print(f"✅ Found image description: {result['image_prompt'][:100]}...")
    
    # If parsing failed, create a fallback
    if not any([name_match, print_match, desc_match]):
        print("⚠️ Could not parse structured format, using fallback")
        # Extract the first line as name
        lines = text.strip().split('\n')
        if lines:
            result["name"] = lines[0].strip()[:100]
        # Create simple image prompt
        result["image_prompt"] = f"A 3D printable {color} {material} object for astronomy and coffee lovers, low-poly design, front view, studio lighting"
    
    return result

def handler(job):
    """Main handler function"""
    print(f"\n🎯 Received job")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        color = input_data.get("color", "gray").strip()
        material = input_data.get("material", "PLA").strip()
        
        print(f"📝 Input: {fun_fact}")
        print(f"🎨 Color: {color}, Material: {material}")
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        if not llm:
            return {
                "status": "error",
                "message": "Model not loaded",
                "debug": f"Path: {MODEL_PATH}, Exists: {os.path.exists(MODEL_PATH)}"
            }
        
        # Generate prompt
        prompt = generate_gift_idea(fun_fact, color, material)
        
        print("🤖 Generating idea...")
        print(f"📝 Prompt length: {len(prompt)} chars")
        
        start_time = time.time()
        
        # Generate response - NO stop parameter, let it complete
        response = llm(
            prompt,
            max_tokens=500,      # Enough for structured response
            temperature=0.7,
            top_p=0.9,
            echo=False          # Don't include prompt in response
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation took: {generation_time:.2f} seconds")
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"📄 Raw response ({len(raw_response)} chars):")
        print("-" * 40)
        print(raw_response[:500] + ("..." if len(raw_response) > 500 else ""))
        print("-" * 40)
        
        # Parse the response
        parsed = parse_response(raw_response)
        
        # Ensure image_prompt is not empty
        if not parsed["image_prompt"] or len(parsed["image_prompt"]) < 20:
            parsed["image_prompt"] = f"A 3D printable {color} {material} object called '{parsed['name']}', low-poly design, front view, studio lighting, clean background"
        
        print(f"✅ Final idea: {parsed['name']}")
        print(f"✅ Image prompt: {parsed['image_prompt'][:100]}...")
        
        return {
            "status": "success",
            "idea": {
                "name": parsed["name"],
                "printability": parsed["printability"],
                "image_prompt": parsed["image_prompt"],
                "fun_fact": fun_fact,
                "material": material,
                "color": color
            },
            "generation_time": f"{generation_time:.2f}s",
            "model": "Qwen2.5-1.5B-Instruct",
            "raw_response_preview": raw_response[:200] + ("..." if len(raw_response) > 200 else "")
        }
        
    except Exception as e:
        print(f"❌ Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "type": type(e).__name__}

print("\n🏁 Starting RunPod serverless handler...")
print("Ready to generate 3D printable gift ideas! 🎁")
print("\n📝 Input format:")
print('''{
  "input": {
    "fun_fact": "loves astronomy and coffee",
    "color": "gray",
    "material": "PLA"
  }
}''')

runpod.serverless.start({"handler": handler})