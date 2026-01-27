# handler.py - DEBUG VERSION
import os
import sys
import time

print("=" * 60)
print("🔍 DEBUG STARTING")
print("=" * 60)

# 1. Check Python and imports
print(f"\n🐍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"📋 Files in directory: {os.listdir('.')}")

# 2. Check root directory
print("\n📁 ROOT DIRECTORY (/):")
for item in sorted(os.listdir('/')):
    if os.path.isdir(os.path.join('/', item)):
        print(f"  📁 {item}/")
    else:
        print(f"  📄 {item}")

# 3. Check common mount points
print("\n🔍 Checking for network volume mounts:")
mount_points = ['/workspace', '/model', '/volume', '/data', '/mnt']
for mp in mount_points:
    if os.path.exists(mp):
        print(f"✅ Found: {mp}")
        try:
            contents = os.listdir(mp)
            print(f"   Contents ({len(contents)} items): {contents}")
        except:
            print(f"   (cannot list)")
    else:
        print(f"❌ Missing: {mp}")

# 4. Try to import runpod
print("\n🔍 Testing imports:")
try:
    import runpod
    print("✅ runpod imported successfully")
    print(f"   Version: {runpod.__version__}")
except Exception as e:
    print(f"❌ runpod import failed: {e}")

try:
    from llama_cpp import Llama
    print("✅ llama_cpp imported successfully")
except Exception as e:
    print(f"❌ llama_cpp import failed: {e}")

# 5. Keep container alive
print("\n" + "=" * 60)
print("⏳ Container will stay alive for debugging...")
print("Check logs for this output!")
print("=" * 60)

# Sleep forever so we can see logs
while True:
    time.sleep(10)
    print("Still alive...")