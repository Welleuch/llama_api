# handler.py - FIXED WITH BETTER PARSING
import runpod
from llama_cpp import Llama
import os
import sys
import time
import json

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
    
    prompt = f"""Create a decorative 3D printable object for a desk.

PERSON INTERESTS: {fun_fact}
MATERIAL: {color} {material}
PRINTING: FDM

COMBINE: astronomy + coffee
TYPE: decorative desk object
STYLE: low-poly 3D model

EXAMPLES:
- "loves cats and surfing" → "Surfing cat figurine"
- "gardening and astronomy" → "Planet-shaped succulent planter"

YOUR RESPONSE MUST BE IN THIS EXACT FORMAT:

IDEA: [creative name]
DESC: [one sentence description]
IMG: [visual description for AI image generator, max 25 words]

NOW CREATE FOR: "{fun_fact}" """
    
    return prompt

def extract_from_response(text, color, material):
    """Extract components from response with fallbacks"""
    
    # Default fallbacks
    idea = f"{color.title()} {material} Gift"
    desc = f"A decorative {material} object for {color} printing"
    img_prompt = f"low-poly {color} {material} decorative object, front view, studio lighting"
    
    # Try to extract IDEA
    lines = text.strip().split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for IDEA: pattern
        if line.upper().startswith('IDEA:'):
            idea = line[5:].strip().strip('"').strip("'")
            # If we have DESC on next line, use it
            if i+1 < len(lines) and lines[i+1].strip().upper().startswith('DESC:'):
                desc = lines[i+1].strip()[5:].strip().strip('"').strip("'")
            # If we have IMG on next+1 line, use it
            if i+2 < len(lines) and lines[i+2].strip().upper().startswith('IMG:'):
                img_prompt = lines[i+2].strip()[4:].strip().strip('"').strip("'")
            break
    
    # If we didn't find IDEA: pattern, try other patterns
    if idea == f"{color.title()} {material} Gift":
        # Look for any creative phrase in first few lines
        for line in lines[:3]:
            if line.strip() and not any(x in line.upper() for x in ['IDEA:', 'DESC:', 'IMG:', 'FOR:']):
                idea = line.strip().strip('"').strip("'")
                # Create a simple description
                words = fun_fact.split()[-3:] if 'fun_fact' in locals() else ['object']
                desc = f"A decorative {' '.join(words)} {material} object"
                # Create image prompt
                img_prompt = f"low-poly {idea.lower()}, {color} {material}, front view, 3D printable"
                break
    
    # Clean up image prompt
    img_prompt = img_prompt.replace('"', '').replace("'", "")
    # Remove any explanations
    sentences = img_prompt.split('.')
    if len(sentences) > 1:
        # Take only the first sentence (visual description)
        img_prompt = sentences[0].strip()
    
    # Ensure image prompt includes key elements
    if color not in img_prompt.lower():
        img_prompt = f"{color} {img_prompt}"
    if material not in img_prompt.lower():
        img_prompt = f"{material} {img_prompt}"
    if 'low-poly' not in img_prompt.lower():
        img_prompt = f"low-poly {img_prompt}"
    
    # Limit length
    words = img_prompt.split()
    if len(words) > 30:
        img_prompt = ' '.join(words[:30])
    
    return idea, desc, img_prompt

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
            return {"status": "error", "message": "Model not loaded"}
        
        # Generate prompt
        prompt = generate_gift_idea(fun_fact, color, material)
        
        print("🤖 Generating...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=150,      # Keep it short
            temperature=0.9,     # More creative
            top_p=0.95,
            echo=False,
            stop=["\n\n", "FOR:", "Now create", "Example:"]  # Stop sequences
        )
        
        generation_time = time.time() - start_time
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"📄 Raw response:\n{raw_response}")
        print("-" * 40)
        
        # Extract components
        idea, desc, img_prompt = extract_from_response(raw_response, color, material)
        
        # Create a better image prompt if it's still generic
        if img_prompt == f"low-poly {color} {material} decorative object, front view, studio lighting":
            # Create from the idea
            img_prompt = f"low-poly {idea.lower()}, {color} {material}, front view, 3D printable desk object, studio lighting"
        
        print(f"✅ Extracted Idea: {idea}")
        print(f"✅ Description: {desc}")
        print(f"✅ Image Prompt: {img_prompt}")
        
        return {
            "status": "success",
            "user_display": {
                "title": idea,
                "description": desc
            },
            "image_generation": {
                "prompt": img_prompt,
                "color": color,
                "material": material,
                "style": "low-poly 3D model"
            },
            "fun_fact": fun_fact,
            "generation_time": f"{generation_time:.2f}s",
            "model": "Qwen2.5-1.5B-Instruct",
            "debug": {
                "raw_response_preview": raw_response[:100]
            }
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

print("\n🏁 Starting RunPod serverless handler...")
print("Ready to generate 3D printable gift ideas! 🎁")

runpod.serverless.start({"handler": handler})