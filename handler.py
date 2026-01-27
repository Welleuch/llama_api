# handler.py - ULTRA SIMPLE APPROACH
import runpod
from llama_cpp import Llama
import os
import sys
import time

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
            n_ctx=2048,
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

def generate_gift_idea(fun_fact):
    """Generate a 3D printable gift idea - ULTRA SIMPLE PROMPT"""
    
    prompt = f"""You are a 3D printing expert. Design a decorative gray PLA object for someone who loves {fun_fact}.

Combine elements from their interests into ONE decorative object.

IMPORTANT: The object must be:
- One solid piece (no assembly)
- Printable with minimal supports
- No overhangs over 45 degrees
- No thin walls under 2mm
- Desk sized (under 15cm)

Give your answer in this exact format:

Creative name: [Name of the object]

Visual description for AI image generator: [Describe the object's appearance for creating a 3D render image. Include shape, style, key features. Mention it's a gray PLA 3D printable object.]"""
    
    return prompt

def handler(job):
    """Main handler function"""
    print(f"\n🎯 Received job")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        
        print(f"📝 Input: {fun_fact}")
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        if not llm:
            return {"status": "error", "message": "Model not loaded"}
        
        # Generate prompt
        prompt = generate_gift_idea(fun_fact)
        
        print("🤖 Generating...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=400,
            temperature=0.8,
            top_p=0.9,
            echo=False
        )
        
        generation_time = time.time() - start_time
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"\n📄 Raw response:\n{raw_response}")
        print("-" * 50)
        
        # SIMPLE PARSING - just split by lines
        lines = [line.strip() for line in raw_response.split('\n') if line.strip()]
        
        # Find name (look for line with "Creative name:" or similar)
        name = "3D Printed Gift"
        visual_desc = "gray PLA decorative object, low-poly style, front view"
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Look for name
            if any(phrase in line_lower for phrase in ["creative name", "name:", "idea:", "object:"]):
                # Extract name after colon
                if ':' in line:
                    name = line.split(':', 1)[1].strip()
                else:
                    name = line
                # Clean up
                name = name.replace('"', '').replace("'", "").strip()
            
            # Look for visual description
            if any(phrase in line_lower for phrase in ["visual description", "description:", "describe", "image prompt"]):
                if ':' in line:
                    visual_desc = line.split(':', 1)[1].strip()
                else:
                    visual_desc = line
                # Clean up
                visual_desc = visual_desc.replace('"', '').replace("'", "").strip()
                
                # If description is short, try to get more from next lines
                if len(visual_desc.split()) < 10 and i+1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line and not any(x in next_line.lower() for x in ["creative name", "name:"]):
                        visual_desc += " " + next_line
        
        # If visual_desc is still generic, create a better one
        if visual_desc == "gray PLA decorative object, low-poly style, front view" or len(visual_desc.split()) < 15:
            # Create from the name and fun_fact
            visual_desc = f"low-poly {name.lower()}, gray PLA material, 3D printable decorative object, front view, studio lighting"
        
        # Ensure visual description includes key elements
        if "gray" not in visual_desc.lower() and "grey" not in visual_desc.lower():
            visual_desc = f"gray {visual_desc}"
        if "pla" not in visual_desc.lower():
            visual_desc = f"PLA {visual_desc}"
        if "3d" not in visual_desc.lower() and "three dimensional" not in visual_desc.lower():
            visual_desc = f"3D printable {visual_desc}"
        
        print(f"\n✅ Results:")
        print(f"Name: {name}")
        print(f"Visual: {visual_desc}")
        
        # Create the text-image prompt that includes DfAM context
        # This goes DIRECTLY to the text-to-image model
        text_image_prompt = f"{visual_desc}. Designed for 3D printing with minimal supports, solid construction, gray PLA material."
        
        return {
            "status": "success",
            "user_output": {
                "name": name,
                "fun_fact": fun_fact,
                "material": "PLA",
                "color": "gray"
            },
            "text_image_prompt": text_image_prompt,  # This goes to SD/DALL-E/etc
            "generation_time": f"{generation_time:.2f}s",
            "model": "Qwen2.5-1.5B-Instruct"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

print("\n🏁 Starting RunPod serverless handler...")
print("Ready to generate 3D printable gift ideas! 🎁")

runpod.serverless.start({"handler": handler})