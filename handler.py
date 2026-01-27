# handler.py - SIMPLIFIED & FIXED
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

def generate_gift_idea(fun_fact):
    """Generate a 3D printable gift idea - SIMPLE PROMPT"""
    
    prompt = f"""You are a creative product designer and 3D-printing expert.

Create a 3D printed gift made completely with PLA filament of gray color.

The person loves: {fun_fact}

Create a unique gift idea that combines these interests and is decorative for a desk.

IMPORTANT PRINTING RULES:
- Print with minimal or no support material
- No thin walls (minimum 2mm thickness)
- No separate parts - must be one continuous object
- Avoid overhangs greater than 45 degrees
- No electronics or moving parts
- Size under 15cm

GOOD IDEAS:
- Figurines that combine interests
- Desk organizers with themed designs
- Decorative holders or stands
- Low-poly sculptures

Now generate ONE gift idea with:
1. A creative name
2. A brief description
3. A visual description for AI image generation

Format your answer like this:

NAME: [Creative name here]

DESCRIPTION: [What it is and how it combines the interests]

VISUAL: [Detailed visual description for image generation. Describe shape, style, features. Mention it's a gray PLA 3D printable object.]

For: {fun_fact}"""
    
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
        print(f"📝 Prompt length: {len(prompt)} chars")
        
        print("🤖 Generating...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=350,      # Enough for all three parts
            temperature=0.7,     # Balanced creativity
            top_p=0.9,
            echo=False
        )
        
        generation_time = time.time() - start_time
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"\n📄 Full response:\n{raw_response}")
        print("-" * 50)
        
        # Parse the response
        lines = raw_response.split('\n')
        name = "3D Printed Gift"
        description = "A decorative object"
        visual = "gray PLA decorative object, low-poly style, front view"
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if line.upper().startswith('NAME:'):
                name = line[5:].strip()
                # Look ahead for description
                for j in range(i+1, min(i+3, len(lines))):
                    if lines[j].strip().upper().startswith('DESCRIPTION:'):
                        description = lines[j].strip()[12:].strip()
                        # Look ahead for visual
                        for k in range(j+1, min(j+3, len(lines))):
                            if lines[k].strip().upper().startswith('VISUAL:'):
                                visual = lines[k].strip()[7:].strip()
                                break
                        break
                break
        
        # Clean up visual description
        visual = visual.replace('"', '').replace("'", "")
        # Ensure it mentions gray PLA
        if "gray" not in visual.lower() and "grey" not in visual.lower():
            visual = f"gray PLA {visual}"
        if "PLA" not in visual.upper():
            visual = f"PLA {visual}"
        
        # Remove any meta instructions from visual
        visual = visual.split('.')[0].strip()
        
        print(f"\n✅ Parsed results:")
        print(f"Name: {name}")
        print(f"Description: {description}")
        print(f"Visual: {visual}")
        
        return {
            "status": "success",
            "idea": {
                "name": name,
                "description": description,
                "visual_prompt": visual,
                "fun_fact": fun_fact,
                "material": "PLA",
                "color": "gray",
                "printing_notes": "Designed for minimal supports, one continuous object"
            },
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
print("\n📝 Input format (simple):")
print('''{
  "input": {
    "fun_fact": "loves astronomy and coffee"
  }
}''')

runpod.serverless.start({"handler": handler})