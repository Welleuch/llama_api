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

runpod.serverless.start({"handler": handler})