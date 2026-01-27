# handler.py - DEBUG VERSION
import runpod
import os
import sys
import time

print("=" * 60)
print("🔍 DEBUG: Finding Model Location")
print("=" * 60)

# Check ALL directories in root
print("\n📁 FULL ROOT DIRECTORY SCAN:")
for item in sorted(os.listdir('/')):
    full_path = os.path.join('/', item)
    if os.path.isdir(full_path):
        print(f"\n📁 {item}/")
        try:
            contents = os.listdir(full_path)
            if contents:
                # Show first 10 items
                for content in contents[:10]:
                    content_path = os.path.join(full_path, content)
                    if os.path.isfile(content_path):
                        size = os.path.getsize(content_path)
                        if content.endswith('.gguf'):
                            print(f"  ⭐ {content} ({size / (1024**3):.2f} GB) <- GGUF FILE!")
                        else:
                            print(f"  📄 {content} ({size / 1024:.1f} KB)")
                    else:
                        print(f"  📁 {content}/")
                if len(contents) > 10:
                    print(f"  ... and {len(contents) - 10} more items")
            else:
                print("  (empty)")
        except Exception as e:
            print(f"  (cannot list: {e})")
    else:
        size = os.path.getsize(full_path)
        print(f"📄 {item} ({size / 1024:.1f} KB)")

# Special check for network volume
print("\n🔍 CHECKING COMMON MOUNT POINTS:")
mount_points = ['/workspace', '/model', '/volume', '/data', '/mnt', '/runpod']
for mp in mount_points:
    if os.path.exists(mp):
        print(f"✅ {mp} EXISTS")
        try:
            contents = os.listdir(mp)
            print(f"   Contents: {contents}")
            
            # Look for GGUF files
            gguf_files = [f for f in contents if f.endswith('.gguf')]
            if gguf_files:
                print(f"   🎯 FOUND GGUF FILES: {gguf_files}")
        except:
            print(f"   (cannot list)")
    else:
        print(f"❌ {mp} does not exist")

print("\n" + "=" * 60)
print("🔍 Looking for ANY .gguf files anywhere...")
print("=" * 60)

# Search recursively for GGUF files (limited depth)
def find_gguf_files(start_path, max_depth=3):
    gguf_files = []
    for root, dirs, files in os.walk(start_path):
        depth = root.count(os.sep) - start_path.count(os.sep)
        if depth > max_depth:
            continue
        
        for file in files:
            if file.endswith('.gguf'):
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                gguf_files.append((full_path, size))
    
    return gguf_files

# Search in likely locations
search_paths = ['/', '/workspace', '/model', '/volume', '/data', '/mnt', '/runpod']
all_gguf_files = []

for path in search_paths:
    if os.path.exists(path):
        print(f"\nSearching in {path}:")
        files = find_gguf_files(path, max_depth=2)
        if files:
            for file_path, size in files:
                print(f"  ✅ Found: {file_path} ({size / (1024**3):.2f} GB)")
                all_gguf_files.append((file_path, size))
        else:
            print(f"  No GGUF files found")

print("\n" + "=" * 60)
if all_gguf_files:
    print(f"🎯 Found {len(all_gguf_files)} GGUF file(s)!")
    for file_path, size in all_gguf_files:
        print(f"  - {file_path} ({size / (1024**3):.2f} GB)")
else:
    print("❌ No GGUF files found anywhere!")
    print("\n💡 PROBLEM: Network volume not mounted or model not uploaded")
    print("   Check: 1. Volume attached to endpoint")
    print("          2. Model uploaded to volume")
    print("          3. Correct mount path")

# Simple handler for debugging
def handler(job):
    return {
        "status": "debug",
        "message": "Debug scan complete",
        "found_gguf_files": [f[0] for f in all_gguf_files] if all_gguf_files else "none",
        "root_dirs": [d for d in os.listdir('/') if os.path.isdir(os.path.join('/', d))]
    }

print("\n🏁 Starting debug server...")
runpod.serverless.start({"handler": handler})