# handler.py - ULTRA SIMPLE TEST
print("=== SIMPLE TEST STARTING ===")

# Try to import runpod
try:
    import runpod
    print("✅ runpod imported")
except Exception as e:
    print(f"❌ runpod import failed: {e}")
    import traceback
    traceback.print_exc()

# Simple handler
def handler(job):
    return {"status": "test", "message": "Hello from handler"}

print("Starting runpod server...")
runpod.serverless.start({"handler": handler})