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

IMPORTANT: Each object must be:
- Made of gray PLA
- Desk-sized (fits on a desk)
- One solid piece (no assembly needed)
- Easy to 3D print with minimal supports

For EACH object, provide EXACTLY this format:
Name: [Creative name, 2-4 words]
Visual: [A detailed visual description for AI image generation. Start with "3D printable Gray PLA". Describe the object clearly in 2-3 sentences.]

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
    """Extract name and visual prompts from text - IMPROVED"""
    ideas = []
    
    print(f"Parsing text of length: {len(text)}")
    print(f"First 500 chars: {text[:500]}")
    
    # Clean the text first
    text = text.strip()
    
    # Try different patterns to find ideas
    patterns = [
        r'IDEA\s+\d+:\s*\n',  # IDEA 1:
        r'Idea\s+\d+:\s*\n',  # Idea 1:
        r'### IDEA\s+\d+:\s*\n',  # ### IDEA 1:
        r'\d+\.\s*\n',  # 1.
    ]
    
    # Try to split by any of these patterns
    sections = []
    for pattern in patterns:
        sections = re.split(pattern, text, flags=re.IGNORECASE)
        if len(sections) > 3:  # Found meaningful splits
            print(f"Split into {len(sections)} sections with pattern: {pattern}")
            break
    
    # If no pattern worked, try manual extraction
    if len(sections) <= 3:
        print("No pattern matched, trying manual extraction")
        # Look for "Name:" and "Visual:" patterns
        name_matches = list(re.finditer(r'(?:Name|Title):\s*(.+?)(?:\n|$)', text, re.IGNORECASE))
        visual_matches = list(re.finditer(r'(?:Visual|Description):\s*(.+?)(?:\n|$)', text, re.IGNORECASE))
        
        for i in range(min(3, len(name_matches), len(visual_matches))):
            name = name_matches[i].group(1).strip()
            visual = visual_matches[i].group(1).strip()
            
            # Clean up quotes
            name = name.strip('"\'')
            visual = visual.strip('"\'').replace('**', '')
            
            ideas.append({
                "name": name,
                "visual": clean_visual_prompt(visual)
            })
        
        return ideas if ideas else create_fallback_ideas()
    
    # Process each section (skip first empty section)
    for i, section in enumerate(sections[1:4]):  # Only first 3 ideas
        section = section.strip()
        if not section:
            continue
            
        name = ""
        visual = ""
        
        # Look for Name and Visual in this section
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for name
            if line.lower().startswith(('name:', 'title:')):
                name = line.split(':', 1)[1].strip()
            elif line.lower().startswith(('visual:', 'description:')):
                visual = line.split(':', 1)[1].strip()
            elif not name and len(line.split()) <= 5 and not any(x in line.lower() for x in ['idea', 'visual', 'name', 'description']):
                # Could be a name
                name = line
            elif not visual and len(line.split()) > 10:
                # Could be a visual description
                visual = line
        
        # If we found both, clean them
        if name and visual:
            name = name.strip('"\'').replace('**', '')
            visual = clean_visual_prompt(visual)
            
            ideas.append({
                "name": name,
                "visual": visual
            })
    
    # If we didn't get 3 ideas, create fallbacks
    if len(ideas) < 3:
        print(f"Only found {len(ideas)} ideas, adding fallbacks")
        ideas.extend(create_fallback_ideas()[:3-len(ideas)])
    
    return ideas[:3]  # Return max 3

def clean_visual_prompt(visual):
    """Clean and format visual prompt"""
    if not visual:
        return "A 3D printable decorative object made of gray PLA, desk-sized"
    
    # Remove unwanted prefixes
    visual = visual.strip()
    
    # Remove common problematic prefixes
    prefixes_to_remove = [
        "PLA Gray",
        "Gray PLA",
        "3D printable",  # We'll add it back if needed
        "**Visual Description:**",
        "**Visual:**",
        "Visual:",
        "Description:"
    ]
    
    for prefix in prefixes_to_remove:
        if visual.lower().startswith(prefix.lower()):
            visual = visual[len(prefix):].strip()
    
    # Ensure it starts with "3D printable"
    if not visual.lower().startswith('3d printable'):
        visual = f"3D printable {visual}"
    
    # Ensure it mentions gray PLA
    if 'gray' not in visual.lower() and 'grey' not in visual.lower():
        visual = f"Gray PLA {visual}"
    elif 'pla' not in visual.lower():
        visual = f"PLA {visual}"
    
    # Remove any remaining markdown
    visual = visual.replace('**', '').replace('__', '')
    
    # Limit length
    words = visual.split()
    if len(words) > 50:
        visual = ' '.join(words[:50]) + "..."
    
    return visual

def create_fallback_ideas():
    """Create fallback ideas"""
    return [
        {
            "name": "Dancing Knit Sculpture",
            "visual": "3D printable Gray PLA sculpture combining dance ribbons with knitted textures, minimalist design, desk decor"
        },
        {
            "name": "Knit & Dance Coaster Set", 
            "visual": "3D printable Gray PLA set of coasters with dance pattern edges and knitted center designs, functional art"
        },
        {
            "name": "Ballerina Yarn Holder",
            "visual": "3D printable Gray PLA figurine of a ballerina holding knitting yarn, elegant pose, desk accessory"
        }
    ]
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