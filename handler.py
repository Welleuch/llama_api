# handler.py - SIMPLIFIED VERSION
import runpod
from llama_cpp import Llama
import os
import sys
import time
import re

print("=" * 60)
print("🚀 3D PRINTING GIFT IDEA GENERATOR")
print("=" * 60)

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
            n_ctx=1024,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False
        )
        print("✅ Model loaded successfully!")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        llm = None
else:
    print("❌ Model file not found!")

def generate_gift_idea(fun_fact, color="gray", material="PLA"):
    """Generate a 3D printable gift idea"""
    
    prompt = f"""Create a decorative 3D printable object for a desk or sideboard.

THE PERSON: {fun_fact}
MATERIAL: {color} {material}
PRINTING: FDM (no supports if possible)

REQUIREMENTS:
1. Combine something from astronomy with something from coffee
2. Must be decorative for desk/sideboard (not functional)
3. Must be one solid object that prints easily
4. Size: under 15cm in any dimension

EXAMPLES:
- For "loves cats and surfing": "Surfing cat figurine"
- For "gardening and astronomy": "Planet-shaped succulent planter"

FORMAT YOUR ANSWER:

IDEA: [One short creative name]

DESCRIPTION: [One sentence - what it looks like]

IMAGE_PROMPT: [Visual description ONLY for AI image generator. Include: shape, style (low-poly), material ({color} {material}), front view. MAX 30 words.]

FOR: "{fun_fact}" """
    
    return prompt

def parse_response(text):
    """Extract the three parts"""
    result = {
        "idea": "3D Printed Gift",
        "description": "A decorative object",
        "image_prompt": f"low-poly {color} {material} decorative object, front view"
    }
    
    # Clean the text
    text = text.strip()
    
    # Extract IDEA
    idea_match = re.search(r'IDEA:\s*(.+?)(?=DESCRIPTION:|IMAGE_PROMPT:|$)', text, re.IGNORECASE)
    if idea_match:
        result["idea"] = idea_match.group(1).strip().strip('"')
    
    # Extract DESCRIPTION
    desc_match = re.search(r'DESCRIPTION:\s*(.+?)(?=IMAGE_PROMPT:|$)', text, re.IGNORECASE)
    if desc_match:
        result["description"] = desc_match.group(1).strip().strip('"')
    
    # Extract IMAGE_PROMPT
    img_match = re.search(r'IMAGE_PROMPT:\s*(.+?)$', text, re.IGNORECASE)
    if img_match:
        result["image_prompt"] = img_match.group(1).strip().strip('"')
    
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
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        if not llm:
            return {"status": "error", "message": "Model not loaded"}
        
        # Generate prompt
        prompt = generate_gift_idea(fun_fact, color, material)
        
        print("🤖 Generating...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=200,      # SHORT response!
            temperature=0.8,     # More creative
            top_p=0.9,
            echo=False
        )
        
        generation_time = time.time() - start_time
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"📄 Raw: {raw_response[:100]}...")
        
        # Parse
        parsed = parse_response(raw_response)
        
        # Clean up image prompt - remove any explanations
        img_prompt = parsed["image_prompt"]
        # Remove anything that sounds like an explanation
        img_prompt = re.sub(r'(this|which|because|so that|allowing|making it).*', '', img_prompt, flags=re.IGNORECASE)
        img_prompt = re.sub(r'\s+', ' ', img_prompt).strip()
        
        # Ensure it's not too long
        if len(img_prompt.split()) > 40:
            words = img_prompt.split()[:40]
            img_prompt = ' '.join(words) + "..."
        
        print(f"✅ Idea: {parsed['idea']}")
        print(f"✅ Image prompt: {img_prompt[:80]}...")
        
        return {
            "status": "success",
            "user_display": {
                "title": parsed["idea"],
                "description": parsed["description"]
            },
            "image_generation": {
                "prompt": img_prompt,
                "color": color,
                "material": material
            },
            "fun_fact": fun_fact,
            "generation_time": f"{generation_time:.2f}s"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

print("\n🏁 Starting...")
runpod.serverless.start({"handler": handler})