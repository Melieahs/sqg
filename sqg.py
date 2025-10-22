import os
import sys
import platform
import requests
from pathlib import Path

BASE_URL = "http://192.168.1.11:18080/packages"

def detect_os():
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    elif system.startswith("CYGWIN") or system.startswith("MINGW") or system == "Windows":
        return "windows"
    else:
        return "unknown"

def get_download_dir():
    home = Path.home()
    return home / "Downloads" / "sqg"

def fetch_index(os_dir):
    index_url = f"{BASE_URL}/{os_dir}/index.txt"
    print(f"📥 Fetching index from {index_url}...")
    try:
        response = requests.get(index_url)
        response.raise_for_status()
        return response.text.strip().splitlines()
    except Exception as e:
        print(f"❌ Failed to fetch index: {e}")
        sys.exit(1)

def get_pkg(pkg):
    if not pkg:
        print("❗ Missing package name")
        print("Usage: sqg get <package-name>[@version]")
        sys.exit(1)

    os_dir = detect_os()
    index_lines = fetch_index(os_dir)

    if "@" in pkg:
        name, version = pkg.split("@", 1)
        file_line = next((line for line in index_lines if line.startswith(f"{name}={version}=")), "")
    else:
        name = pkg
        candidates = [line for line in index_lines if line.startswith(f"{name}=")]
        candidates.sort(key=lambda x: x.split("=")[1], reverse=True)
        file_line = candidates[0] if candidates else ""

    if not file_line:
        print(f"❌ Package '{pkg}' not found in index.")
        suggestions = sorted(set(line.split("=")[0] for line in index_lines if name.lower() in line.lower()))
        if suggestions:
            print("🔍 Did you mean:")
            for s in suggestions[:5]:
                print(f"  - {s}")
        sys.exit(1)

    parts = file_line.split("=")
    version = parts[1]
    file_name = parts[2]
    url = f"{BASE_URL}/{os_dir}/{file_name}"

    download_dir = get_download_dir()
    download_dir.mkdir(parents=True, exist_ok=True)
    dest_path = download_dir / file_name

    print(f"⬇️ Downloading {name} (version {version}): {file_name}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ Downloaded to: {dest_path}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        sys.exit(1)

def list_index():
    os_dir = detect_os()
    index_lines = fetch_index(os_dir)
    print(f"📦 Available packages for [{os_dir}]:")
    for line in sorted(index_lines):
        parts = line.split("=")
        if len(parts) >= 2:
            print(f"  {parts[0]:20} {parts[1]}")

def update_index():
    script_path = "/vol3/1000/packages/index.sh"
    if not os.path.exists(script_path):
        print(f"❌ Index script not found: {script_path}")
        sys.exit(1)
    print("🔄 Updating index files...")
    os.system(f"bash {script_path}")

def main():
    print("🚀 Running sqg...")
    print("🧾 Arguments:", sys.argv)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  sqg get <package>[@version]   Download a package")
        print("  sqg index                     List available packages")
        print("  sqg update                    Regenerate index files")
        sys.exit(1)

    cmd = sys.argv[1]
    pkg = sys.argv[2] if len(sys.argv) > 2 else None

    if cmd == "get":
        get_pkg(pkg)
    elif cmd == "index":
        list_index()
    elif cmd == "update":
        update_index()
    else:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
