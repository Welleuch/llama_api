# handler.py - SINGLE HIGH-QUALITY IDEA (BEST VERSION)
import runpod
from llama_cpp import Llama
import os
import sys
import time

print("=" * 60)
print("🚀 3D PRINTING GIFT IDEA GENERATOR")
print("(Single High-Quality Idea Version)")
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

def generate_high_quality_idea(fun_fact):
    """Generate ONE high-quality, specific idea"""
    
    prompt = f"""You are designing a 3D printable decorative object for a desk.

PERSON'S INTERESTS: {fun_fact}
MATERIAL: Gray PLA plastic
PRINTING METHOD: FDM (Fused Deposition Modeling)

CREATE ONE SPECIFIC OBJECT that creatively combines elements from their interests.

OBJECT REQUIREMENTS:
• Must be ONE solid object (no assembly)
• Printable with minimal or no supports
• No overhangs greater than 45 degrees
• No thin walls (minimum 2mm thickness)
• Desk-sized (under 15cm tall/wide)
• Decorative, not functional
• Visually interesting from the front

BRAINSTORM EXAMPLE:
For "loves coffee and cats":
• A cat-shaped coffee cup holder
• A coaster with cat paw prints and coffee bean patterns
• A pen holder shaped like a sleeping cat next to a coffee mug

YOUR TASK:
1. Think of ONE creative, specific object
2. Describe it in detail for an AI image generator
3. Make sure it follows all printing rules

FORMAT YOUR RESPONSE:

OBJECT: [Creative, specific name]

DESCRIPTION: [Detailed visual description for AI image generation. Be specific about shapes, features, style. Mention it's a gray PLA 3D printable object. 3-5 sentences.]

Now create for: "{fun_fact}"
"""
    
    return prompt

def handler(job):
    """Main handler function - Returns ONE high-quality idea"""
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
        prompt = generate_high_quality_idea(fun_fact)
        
        print("🤖 Generating high-quality idea...")
        start_time = time.time()
        
        response = llm(
            prompt,
            max_tokens=450,      # Enough for detailed description
            temperature=0.75,    # Balanced creativity
            top_p=0.9,
            echo=False
        )
        
        generation_time = time.time() - start_time
        
        raw_response = response['choices'][0]['text'].strip()
        print(f"\n📄 Raw response:\n{raw_response}")
        print("-" * 50)
        
        # Parse the response
        lines = [line.strip() for line in raw_response.split('\n') if line.strip()]
        
        name = f"3D Printed Gift for {fun_fact.split()[-1] if len(fun_fact.split()) > 1 else 'Friend'}"
        description = ""
        
        # Look for OBJECT: and DESCRIPTION: markers
        found_object = False
        found_description = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            if line_lower.startswith('object:'):
                name = line[7:].strip().strip('"').strip("'")
                found_object = True
            
            elif line_lower.startswith('description:'):
                description = line[12:].strip().strip('"').strip("'")
                found_description = True
                
                # Try to get more description from following lines
                for j in range(i+1, min(i+4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.lower().startswith(('object:', 'description:', 'name:')):
                        description += " " + next_line
            
            elif not found_object and len(line) > 10 and ':' not in line:
                # If no OBJECT: found, use first substantial line as name
                name = line[:80]
                found_object = True
        
        # If no proper description was found, use the entire response (excluding name)
        if not description or len(description.split()) < 15:
            # Combine all lines except the name line
            all_text = ' '.join(lines)
            if name in all_text:
                description = all_text.replace(name, '').strip()
            else:
                description = all_text
        
        # Clean and enhance the description
        description = description.replace('"', '').replace("'", "").strip()
        
        # Ensure it mentions key elements
        desc_lower = description.lower()
        if "gray" not in desc_lower and "grey" not in desc_lower:
            description = f"Gray {description}"
        if "pla" not in desc_lower:
            description = f"PLA {description}"
        if "3d" not in desc_lower and "three dimensional" not in desc_lower:
            description = f"3D printable {description}"
        
        # Add DfAM context if not already there
        if "support" not in desc_lower and "print" in desc_lower:
            description += " Designed for 3D printing with minimal supports, solid construction."
        
        # Clean up repetitions
        sentences = description.split('. ')
        unique_sentences = []
        seen = set()
        for sentence in sentences:
            words = sentence.split()[:10]  # First 10 words as key
            key = ' '.join(words).lower()
            if key not in seen:
                unique_sentences.append(sentence)
                seen.add(key)
        
        description = '. '.join(unique_sentences).strip()
        if not description.endswith('.'):
            description += '.'
        
        print(f"\n✅ Parsed results:")
        print(f"Name: {name}")
        print(f"Description length: {len(description.split())} words")
        print(f"First 100 chars: {description[:100]}...")
        
        return {
            "status": "success",
            "idea": {
                "name": name,
                "visual_prompt": description,  # This goes to text-image model
                "fun_fact": fun_fact,
                "material": "PLA",
                "color": "gray",
                "printing_notes": "Designed for FDM printing with minimal supports, one continuous object"
            },
            "generation_time": f"{generation_time:.2f}s",
            "model": "Qwen2.5-1.5B-Instruct",
            "quality": "high"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

print("\n🏁 Starting RunPod serverless handler...")
print("Generating HIGH-QUALITY 3D printable gift ideas! 🎁")
print("\n📝 Input format (simple):")
print('''{
  "input": {
    "fun_fact": "loves coffee and cats"
  }
}''')

runpod.serverless.start({"handler": handler})