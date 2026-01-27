# handler.py - OPTIMIZED FOR 3D PRINTING PIPELINE
import runpod
from llama_cpp import Llama
import os
import sys
import time

print("=" * 60)
print("🚀 3D PRINTING GIFT IDEA GENERATOR")
print("Optimized for: Text → Image → 3D Model Pipeline")
print("Model: Qwen2.5-1.5B-Instruct (Fast & Good Enough)")
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
            n_ctx=2048,      # Increased for longer prompts
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
    
    prompt = f"""You are a professional product designer and 3D-printing expert specializing in FDM printing.

CLIENT REQUEST: Create a 3D printed gift for someone who "{fun_fact}"
Printing Material: {material} filament, {color} color
Printing Process: FDM (Fused Deposition Modeling)

YOUR TASK: Generate ONE excellent 3D printable gift idea that is:
1. USEFUL or DECORATIVE - Related to their interests
2. PRINTABLE WITH FDM - Follows Design for Additive Manufacturing (DfAM) rules
3. VISUALLY APPEALING - Will look good as a rendered image

CRITICAL DESIGN CONSTRAINTS FOR FDM PRINTING:
• MUST print with MINIMAL or NO SUPPORT MATERIAL
• Avoid thin walls (<1mm thickness)
• No bridging over 20mm without supports
• Avoid steep overhangs >45 degrees
• Design as SINGLE CONTINUOUS OBJECT - no assembly required
• No tiny details (<2mm) that won't print well
• Self-supporting geometry preferred
• Optimize for layer adhesion and strength

GOOD PRINTABLE DESIGNS:
• Figurines with angled poses (45° rule)
• Vases, planters with gradual curves
• Wall hooks, bookmarks, keychains
• Desk organizers with rounded edges
• Low-poly animal models
• Geometric shapes that print flat-side-down

BAD DESIGNS (AVOID THESE):
• Floating parts or separate components
• Complex mechanical assemblies
• Electronics housings
• Ultra-thin features
• Large flat horizontal surfaces (warping risk)

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

IDEA NAME: [Creative, descriptive name]

PRINTABILITY: [Beginner/Intermediate/Advanced - based on FDM constraints]

DESCRIPTION FOR IMAGE GENERATION: [Write a detailed visual description for a text-to-image AI. Focus on:
  - Shape, form, silhouette from front view
  - Key visual features and textures
  - Lighting and perspective
  - Style (low-poly, realistic, artistic)
  - Include that it's a 3D printable gray PLA object
  - Describe it as if viewing from front at eye level]

EXAMPLE RESPONSE FOR "loves cats and surfing":
IDEA NAME: Surfing Cat Figurine

PRINTABILITY: Beginner

DESCRIPTION FOR IMAGE GENERATION: A cute stylized cat standing on a surfboard, viewed from front at eye level. The cat has a playful pose with one paw up. The surfboard has wave patterns. Low-poly 3D style, smooth surfaces, solid gray PLA material. Shadows under the surfboard, studio lighting, clean background.

NOW CREATE FOR: "{fun_fact}" with {color} {material} filament"""
    
    return prompt

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
        
        # Generate prompt with DfAM constraints
        prompt = generate_gift_idea(fun_fact, color, material)
        
        print("🤖 Generating 3D printable idea...")
        start_time = time.time()
        
        # Generate response - increased tokens for detailed description
        response = llm(
            prompt,
            max_tokens=800,      # More tokens for detailed description
            temperature=0.7,     # Creative but constrained
            top_p=0.85,          # Slightly more focused
            echo=False,
            stop=["IDEA NAME:", "PRINTABILITY:", "DESCRIPTION FOR IMAGE GENERATION:"]
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation took: {generation_time:.2f} seconds")
        
        result = response['choices'][0]['text'].strip()
        
        # Parse the structured response
        lines = result.split('\n')
        idea_name = ""
        printability = ""
        image_description = ""
        
        current_section = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "IDEA NAME:" in line:
                idea_name = line.replace("IDEA NAME:", "").strip()
                current_section = "name"
            elif "PRINTABILITY:" in line:
                printability = line.replace("PRINTABILITY:", "").strip()
                current_section = "printability"
            elif "DESCRIPTION FOR IMAGE GENERATION:" in line:
                image_description = line.replace("DESCRIPTION FOR IMAGE GENERATION:", "").strip()
                current_section = "description"
            elif current_section == "description" and line:
                image_description += " " + line
        
        # Clean up the image description
        image_description = ' '.join(image_description.split())
        
        print(f"✅ Generated: {idea_name} ({printability} difficulty)")
        
        return {
            "status": "success",
            "idea": {
                "name": idea_name,
                "printability": printability,
                "image_prompt": image_description,
                "fun_fact": fun_fact,
                "material": material,
                "color": color
            },
            "generation_time": f"{generation_time:.2f}s",
            "model": "Qwen2.5-1.5B-Instruct"
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
    "fun_fact": "loves gardening and astronomy",
    "color": "gray",
    "material": "PLA"
  }
}''')

runpod.serverless.start({"handler": handler})