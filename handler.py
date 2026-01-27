# handler.py - MULTIPLE IDEAS WITH STREAMING
import runpod
from llama_cpp import Llama
import os
import sys
import time

print("=" * 60)
print("🚀 3D PRINTING GIFT IDEA GENERATOR - MULTIPLE IDEAS")
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
            n_ctx=4096,  # Increased for multiple ideas
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

def generate_multiple_ideas(fun_fact, num_ideas=5):
    """Generate multiple 3D printable gift ideas"""
    
    prompt = f"""You are a 3D printing expert. Design {num_ideas} different decorative gray PLA objects for someone who loves {fun_fact}.

For EACH idea, combine elements from their interests into ONE decorative object.

IMPORTANT: Each object must be:
- One solid piece (no assembly)
- Printable with minimal supports
- No overhangs over 45 degrees
- No thin walls under 2mm
- Desk sized (under 15cm)
- Visually distinct from the other ideas

Format your response EXACTLY like this:

1. IDEA: [Creative name]
   VISUAL: [Visual description for AI image generator]

2. IDEA: [Creative name]
   VISUAL: [Visual description for AI image generator]

3. IDEA: [Creative name]
   VISUAL: [Visual description for AI image generator]

4. IDEA: [Creative name]
   VISUAL: [Visual description for AI image generator]

5. IDEA: [Creative name]
   VISUAL: [Visual description for AI image generator]

Make each idea unique and creative!"""
    
    return prompt

def parse_ideas_from_response(text):
    """Parse multiple ideas from the response"""
    ideas = []
    lines = text.strip().split('\n')
    
    current_idea = None
    current_visual = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a new idea (starts with number and "IDEA:")
        if any(line.startswith(f"{i}. IDEA:") for i in range(1, 10)):
            # Save previous idea if exists
            if current_idea and current_visual:
                ideas.append({
                    "name": current_idea,
                    "visual_prompt": current_visual
                })
            
            # Start new idea
            parts = line.split('IDEA:', 1)
            if len(parts) > 1:
                current_idea = parts[1].strip()
            else:
                current_idea = line
            current_visual = ""
        
        # Check if this is a visual description line
        elif line.startswith("VISUAL:") or (current_visual == "" and current_idea):
            if line.startswith("VISUAL:"):
                current_visual = line[7:].strip()
            else:
                # Might be continuation of visual description
                if current_visual and current_visual != "":
                    current_visual += " " + line
    
    # Don't forget the last idea
    if current_idea and current_visual:
        ideas.append({
            "name": current_idea,
            "visual_prompt": current_visual
        })
    
    # Clean up and enhance the visual prompts
    for i, idea in enumerate(ideas):
        # Clean up
        idea["name"] = idea["name"].replace('"', '').replace("'", "").strip()
        idea["visual_prompt"] = idea["visual_prompt"].replace('"', '').replace("'", "").strip()
        
        # Ensure it mentions gray PLA and 3D printing
        visual = idea["visual_prompt"]
        if "gray" not in visual.lower() and "grey" not in visual.lower():
            visual = f"gray {visual}"
        if "pla" not in visual.lower():
            visual = f"PLA {visual}"
        if "3d" not in visual.lower() and "three dimensional" not in visual.lower():
            visual = f"3D printable {visual}"
        
        # Add DfAM context
        visual += ". Designed for 3D printing with minimal supports, solid construction."
        
        # Limit length
        words = visual.split()
        if len(words) > 60:
            visual = ' '.join(words[:60]) + "..."
        
        ideas[i]["visual_prompt"] = visual
    
    return ideas

def handler(job):
    """Main handler function - Returns multiple ideas"""
    print(f"\n🎯 Received job")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        num_ideas = min(int(input_data.get("num_ideas", 5)), 10)  # Max 10 ideas
        
        print(f"📝 Input: {fun_fact}")
        print(f"🎯 Number of ideas requested: {num_ideas}")
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        if not llm:
            return {"status": "error", "message": "Model not loaded"}
        
        # Generate prompt for multiple ideas
        prompt = generate_multiple_ideas(fun_fact, num_ideas)
        
        print("🤖 Generating multiple ideas...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=1200,  # More tokens for multiple ideas
            temperature=0.85,  # More creative for variety
            top_p=0.95,
            echo=False
        )
        
        generation_time = time.time() - start_time
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"\n📄 Raw response (first 500 chars):\n{raw_response[:500]}...")
        print("-" * 50)
        
        # Parse the ideas
        ideas = parse_ideas_from_response(raw_response)
        
        # If parsing failed, generate at least one good idea
        if not ideas or len(ideas) < 2:
            print("⚠️ Could not parse multiple ideas, generating single idea...")
            # Fallback to single idea generation
            single_prompt = f"""Create ONE creative 3D printable gift idea for someone who loves {fun_fact}.
            
IDEA: [Name]
VISUAL: [Description for AI image generation]"""
            
            single_response = llm(
                single_prompt,
                max_tokens=300,
                temperature=0.8,
                top_p=0.9
            )
            
            single_text = single_response['choices'][0]['text'].strip()
            # Create at least one idea from this
            ideas = [{
                "name": "Creative Gift Idea",
                "visual_prompt": f"low-poly gray PLA decorative object for {fun_fact}, 3D printable, front view. Designed for 3D printing with minimal supports."
            }]
        
        print(f"\n✅ Generated {len(ideas)} ideas")
        for i, idea in enumerate(ideas, 1):
            print(f"  {i}. {idea['name'][:50]}...")
        
        # Prepare the response with all ideas
        all_ideas = []
        for idea in ideas:
            all_ideas.append({
                "name": idea["name"],
                "visual_prompt": idea["visual_prompt"],
                "material": "PLA",
                "color": "gray"
            })
        
        return {
            "status": "success",
            "fun_fact": fun_fact,
            "total_ideas": len(all_ideas),
            "ideas": all_ideas,  # Array of all ideas
            "generation_time": f"{generation_time:.2f}s",
            "model": "Qwen2.5-1.5B-Instruct"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

print("\n🏁 Starting RunPod serverless handler...")
print("Ready to generate multiple 3D printable gift ideas! 🎁")
print("\n📝 Input format:")
print('''{
  "input": {
    "fun_fact": "loves coffee and cats",
    "num_ideas": 5  // Optional, default is 5
  }
}''')

runpod.serverless.start({"handler": handler})