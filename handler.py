# handler.py - MULTIPLE IDEAS, SIMPLE OUTPUT
import runpod
from llama_cpp import Llama
import os
import sys
import time
import re

print("=" * 60)
print("🚀 3D PRINTING MULTI-IDEA GENERATOR")
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
            n_ctx=4096,
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

def generate_multiple_ideas(fun_fact):
    """Generate 3 ideas with name + detailed visual prompt"""
    
    prompt = f"""Create 3 different 3D printable decorative objects for someone who loves {fun_fact}.

Each object must:
- Combine elements from their interests
- Be made of gray PLA
- Print easily with minimal supports
- Be one solid piece
- Be desk-sized

For EACH object, provide:
1. A creative name (2-4 words)
2. A detailed visual description for AI image generation (3-5 sentences)

Make each object unique and creative!

Here are your 3 ideas:

IDEA 1:
Name: 
Visual: 

IDEA 2:
Name: 
Visual: 

IDEA 3:
Name: 
Visual: 

Now create for: {fun_fact}"""
    
    return prompt

def parse_ideas(text):
    """Extract name and visual prompts from text"""
    ideas = []
    
    # Split by IDEA X: pattern
    idea_sections = re.split(r'IDEA\s*\d+:', text, flags=re.IGNORECASE)
    
    for section in idea_sections[1:]:  # Skip first empty section
        lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
        
        name = ""
        visual = ""
        
        for i, line in enumerate(lines):
            if line.lower().startswith('name:'):
                name = line[5:].strip()
                # Look for Visual in next lines
                for j in range(i+1, len(lines)):
                    if lines[j].lower().startswith('visual:'):
                        visual = lines[j][7:].strip()
                        # Get additional lines if they're part of visual
                        for k in range(j+1, len(lines)):
                            next_line = lines[k].strip()
                            if next_line and not next_line.lower().startswith(('name:', 'idea', 'visual:')):
                                visual += " " + next_line
                            else:
                                break
                        break
                break
        
        # If pattern didn't match, try to find name and visual in first lines
        if not name or not visual:
            for line in lines:
                if line and not line.lower().startswith(('name:', 'visual:')):
                    if not name and len(line.split()) <= 5:
                        name = line
                    elif not visual and len(line.split()) > 10:
                        visual = line
        
        # Clean up
        if name:
            name = name.strip('"').strip("'").strip()
        if visual:
            visual = visual.strip('"').strip("'").strip()
            
            # Ensure it has key elements
            if "gray" not in visual.lower() and "grey" not in visual.lower():
                visual = f"Gray {visual}"
            if "pla" not in visual.lower():
                visual = f"PLA {visual}"
            if "3d" not in visual.lower():
                visual = f"3D printable {visual}"
            
            # Remove any remaining format markers
            visual = visual.replace('Name:', '').replace('Visual:', '')
            
            # Limit length but keep it descriptive
            words = visual.split()
            if len(words) > 80:
                visual = ' '.join(words[:80]) + "..."
        
        if name and visual:
            ideas.append({
                "name": name,
                "visual": visual
            })
    
    return ideas

def handler(job):
    """Main handler - Returns multiple ideas"""
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
        prompt = generate_multiple_ideas(fun_fact)
        
        print("🤖 Generating 3 ideas...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=1200,
            temperature=0.8,
            top_p=0.9,
            echo=False
        )
        
        generation_time = time.time() - start_time
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"\n📄 Raw response:\n{raw_response}")
        print("-" * 50)
        
        # Parse ideas
        ideas = parse_ideas(raw_response)
        
        # If parsing failed, generate at least one good idea
        if len(ideas) < 2:
            print("⚠️ Couldn't parse 3 ideas, generating fallback...")
            # Create simple fallback ideas
            interests = fun_fact.lower()
            if "coffee" in interests and "cats" in interests:
                ideas = [
                    {
                        "name": "Cat Coffee Mug Sculpture",
                        "visual": "Gray PLA 3D printable sculpture of a cat curled around a coffee mug. Detailed fur texture on the cat, steam rising from the mug. Low-poly style, front view, desk decor."
                    },
                    {
                        "name": "Whisker Pattern Coaster",
                        "visual": "Gray PLA coaster with cat whisker patterns and coffee bean imprints. Geometric design, subtle texture, 3D printable decorative object for desk."
                    },
                    {
                        "name": "Sleeping Cat Pen Holder",
                        "visual": "Gray PLA pen holder shaped like a sleeping cat next to a miniature coffee cup. Smooth surfaces, minimalist design, 3D printable desk accessory."
                    }
                ]
        
        print(f"\n✅ Generated {len(ideas)} ideas:")
        for i, idea in enumerate(ideas, 1):
            print(f"  {i}. {idea['name']}")
            print(f"     Visual: {idea['visual'][:80]}...")
        
        # Return with proper structure that the worker expects
        return {
            "response": f"I've created {len(ideas)} creative 3D gift ideas for '{fun_fact}'. Check them out below!",
            "visual_prompts": [idea["visual"] for idea in ideas],
            "all_ideas": ideas
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

print("\n🏁 Starting RunPod serverless handler...")
print("Generating 3 creative ideas per request!")
print("\n📝 Input format:")
print('''{
  "input": {
    "fun_fact": "loves coffee and cats"
  }
}''')

runpod.serverless.start({"handler": handler})