import os
import sys
import re
import platform
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "http://192.168.1.11:5050/packages"
PLATFORMS = ["macos", "linux", "windows", "universal"]

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
    return Path.home() / "Downloads" / "sqg"

def get_local_index_path():
    return get_download_dir() / "config" / "index.txt"

def fetch_index():
    index_path = get_local_index_path()
    if not index_path.exists():
        print(f"Index file not found: {index_path}")
        print("Please run: sqg update")
        sys.exit(1)
    with open(index_path, "r") as f:
        return f.read().strip().splitlines()

def parse_platform_from_args(args):
    for arg in args:
        if arg.startswith("--"):
            plat = arg[2:].lower()
            if plat in PLATFORMS:
                return plat
    return None

def get_pkg(pkg, platform_override=None):
    if not pkg:
        print("Error: Missing package name")
        print("Usage: sqg get <package-name>[@version] [--platform]")
        sys.exit(1)

    current_platform = platform_override or detect_os()
    index_lines = fetch_index()

    candidates = []
    if "@" in pkg:
        name, version = pkg.split("@", 1)
        for line in index_lines:
            parts = line.split("=")
            if len(parts) >= 4 and parts[0] == name and parts[1] == version and parts[3] in [current_platform, "universal"]:
                candidates.append(line)
    else:
        name = pkg
        for line in index_lines:
            parts = line.split("=")
            if len(parts) >= 4 and parts[0] == name and parts[3] in [current_platform, "universal"]:
                candidates.append(line)

        candidates.sort(key=lambda x: x.split("=")[1], reverse=True)

    if not candidates:
        print(f"Package '{pkg}' not found for platform '{current_platform}'.")
        print("It may be available on another platform. Try using --macos, --linux, --windows, or --universal.")
        suggestions = sorted(set(line.split("=")[0] for line in index_lines if name.lower() in line.lower()))
        if suggestions:
            print("Suggestions:")
            for s in suggestions[:5]:
                print(f"  - {s}")
        sys.exit(1)

    line = candidates[0]
    parts = line.split("=")
    name, version, file_name, platform_tag = parts
    url = f"{BASE_URL}/{platform_tag}/{file_name}"

    download_dir = get_download_dir()
    download_dir.mkdir(parents=True, exist_ok=True)
    dest_path = download_dir / file_name

    print(f"Downloading {name} (version {version}) from [{platform_tag}]: {file_name}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with open(dest_path, "wb") as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=file_name,
                ascii=True,
                dynamic_ncols=True,
                file=sys.stdout
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
        print(f"Download complete: {dest_path}")
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
        if dest_path.exists():
            print(f"Partial file saved at: {dest_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)

def list_index():
    index_lines = fetch_index()
    current_platform = detect_os()
    print(f"Available packages for [{current_platform}] and [universal]:")
    for line in sorted(index_lines):
        parts = line.split("=")
        if len(parts) >= 4 and parts[3] in [current_platform, "universal"]:
            print(f"  {parts[0]:20} {parts[1]}")

def update_index():
    config_dir = get_download_dir() / "config"
    index_file = config_dir / "index.txt"
    config_dir.mkdir(parents=True, exist_ok=True)
    entries = []

    print("Generating index from remote server:")
    for plat in PLATFORMS:
        url = f"{BASE_URL}/{plat}/"
        print(f"  - Scanning: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a")
            for link in links:
                fname = link.text.strip()
                if not fname or fname.endswith("/"):
                    continue

                if fname.endswith(".tar.gz"):
                    base = fname[:-7]
                else:
                    base = fname.rsplit(".", 1)[0]

                clean_base = base.lower().replace(" ", "-")
                match = re.search(r"(.+?)[-_ ]v?(\d+\.\d+(?:\.\d+)?)(?:[_\-\s]|$)", clean_base)
                if match:
                    name, version = match.group(1), match.group(2)
                else:
                    name, version = clean_base, "latest"

                entries.append(f"{name}={version}={fname}={plat}")
        except Exception as e:
            print(f"  Failed to scan {url}: {e}")

    def sort_key(line):
        parts = line.split("=")
        name = parts[0]
        version = parts[1]
        return (name, tuple(map(int, version.split("."))) if version != "latest" else (0,))

    entries.sort(key=sort_key)
    with open(index_file, "w") as f:
        f.write("\n".join(entries))

    print(f"Index saved to: {index_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  sqg get <package>[@version] [--platform]   Download a package")
        print("  sqg index                                  List available packages")
        print("  sqg update                                 Generate local index file")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]
    pkg = args[0] if args and not args[0].startswith("--") else None
    platform_override = parse_platform_from_args(args)

    if cmd == "get":
        get_pkg(pkg, platform_override)
    elif cmd == "index":
        list_index()
    elif cmd == "update":
        update_index()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()

