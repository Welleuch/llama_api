# test_local.py - Run this to verify model loads
import os

print("Testing model path...")
model_path = "/model/Llama-3.2-3B-Instruct-IQ3_M.gguf"

if os.path.exists(model_path):
    print(f"✅ Model found at: {model_path}")
    print(f"📏 Size: {os.path.getsize(model_path) / (1024**3):.2f} GB")
else:
    print(f"❌ Model NOT found at: {model_path}")
    
    # Check what's in /model
    if os.path.exists("/model"):
        print("Contents of /model:")
        for item in os.listdir("/model"):
            print(f"  - {item}")
    else:
        print("/model directory doesn't exist!")