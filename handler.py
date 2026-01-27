# handler.py - SIMPLE MULTIPLE IDEAS
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

def generate_single_idea(fun_fact, idea_number=1):
    """Generate ONE idea at a time - simpler for the model"""
    
    prompt = f"""Think of a creative 3D printable gift for someone who loves {fun_fact}.

The gift should combine elements from their interests.
It should be made of gray PLA plastic.
It should print easily with minimal supports.
It should be a decorative object for a desk.

Give me idea number {idea_number}:

Name: [Give it a creative name]
Description: [Describe what it looks like for an AI image generator]"""
    
    return prompt

def handler(job):
    """Main handler function - Generate multiple ideas sequentially"""
    print(f"\n🎯 Received job")
    
    try:
        input_data = job["input"]
        fun_fact = input_data.get("fun_fact", "").strip()
        num_ideas = min(int(input_data.get("num_ideas", 3)), 5)  # Max 5, default 3
        
        print(f"📝 Input: {fun_fact}")
        print(f"🎯 Generating {num_ideas} ideas...")
        
        if not fun_fact:
            return {"error": "Please provide a 'fun_fact'"}
        
        if not llm:
            return {"status": "error", "message": "Model not loaded"}
        
        all_ideas = []
        total_generation_time = 0
        
        # Generate ideas ONE BY ONE
        for i in range(num_ideas):
            print(f"\n💡 Generating idea {i+1}/{num_ideas}...")
            
            prompt = generate_single_idea(fun_fact, i+1)
            
            start_time = time.time()
            
            response = llm(
                prompt,
                max_tokens=200,
                temperature=0.8,
                top_p=0.9,
                echo=False
            )
            
            generation_time = time.time() - start_time
            total_generation_time += generation_time
            
            raw_response = response['choices'][0]['text'].strip()
            print(f"📄 Response {i+1}: {raw_response[:100]}...")
            
            # Simple parsing
            lines = [line.strip() for line in raw_response.split('\n') if line.strip()]
            
            name = f"Idea {i+1}"
            description = f"A decorative 3D printable object for {fun_fact}"
            
            for line in lines:
                line_lower = line.lower()
                if line_lower.startswith('name:'):
                    name = line[5:].strip().strip('"').strip("'")
                elif line_lower.startswith('description:'):
                    description = line[12:].strip().strip('"').strip("'")
                elif ':' not in line and len(line) > 10 and name == f"Idea {i+1}":
                    # If no "Name:" tag found, use the first substantial line as name
                    name = line[:50]
            
            # Enhance the description
            if len(description.split()) < 10:
                description = f"low-poly gray PLA {name.lower()}, 3D printable decorative object, front view"
            
            # Ensure it has key elements
            desc_lower = description.lower()
            if "gray" not in desc_lower and "grey" not in desc_lower:
                description = f"gray {description}"
            if "pla" not in desc_lower:
                description = f"PLA {description}"
            if "3d" not in desc_lower:
                description = f"3D printable {description}"
            
            # Add DfAM context
            description += ". Designed for 3D printing with minimal supports."
            
            # Clean up
            description = ' '.join(description.split()[:50])  # Limit to 50 words
            
            idea = {
                "name": name,
                "visual_prompt": description,
                "material": "PLA",
                "color": "gray",
                "generation_time": f"{generation_time:.2f}s"
            }
            
            all_ideas.append(idea)
            print(f"✅ Idea {i+1}: {name}")
            
            # Optional: small delay between generations
            if i < num_ideas - 1:
                time.sleep(0.5)  # 0.5 second pause
        
        print(f"\n✅ Generated {len(all_ideas)} ideas in {total_generation_time:.2f} seconds")
        
        return {
            "status": "success",
            "fun_fact": fun_fact,
            "total_ideas": len(all_ideas),
            "ideas": all_ideas,
            "total_generation_time": f"{total_generation_time:.2f}s",
            "average_time_per_idea": f"{total_generation_time/len(all_ideas):.2f}s",
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
    "num_ideas": 3  // Optional, 1-5
  }
}''')

runpod.serverless.start({"handler": handler})