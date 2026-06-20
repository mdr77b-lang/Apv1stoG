import base64
import os

def main():
    new_file = "clean_sub.txt"
    dest_file = "public_repo/clean_sub.txt"

    # Read new servers
    if not os.path.exists(new_file):
        print(f"[-] New file {new_file} not found. Nothing to merge.")
        return

    try:
        with open(new_file, "r", encoding="utf-8") as f:
            new_b64 = f.read().strip()
        new_content = base64.b64decode(new_b64).decode("utf-8", errors="ignore")
        new_servers = [line.strip() for line in new_content.splitlines() if line.strip()]
        print(f"[+] Loaded {len(new_servers)} new servers.")
    except Exception as e:
        print(f"[-] Error decoding new subscription: {e}")
        return

    # Read existing servers from the target repo
    existing_servers = []
    if os.path.exists(dest_file):
        try:
            with open(dest_file, "r", encoding="utf-8") as f:
                old_b64 = f.read().strip()
            if old_b64:
                old_content = base64.b64decode(old_b64).decode("utf-8", errors="ignore")
                existing_servers = [line.strip() for line in old_content.splitlines() if line.strip()]
                print(f"[+] Loaded {len(existing_servers)} existing servers from destination.")
        except Exception as e:
            print(f"[-] Warning: Error reading or decoding existing subscription: {e}")
    else:
        print(f"[!] Destination file {dest_file} does not exist yet. It will be created.")

    # Merge and deduplicate, keeping order
    seen = set()
    merged_servers = []
    
    # 1. Add existing servers first to preserve history
    for s in existing_servers:
        if s not in seen:
            seen.add(s)
            merged_servers.append(s)
            
    # 2. Add new unique servers
    added_count = 0
    for s in new_servers:
        if s not in seen:
            seen.add(s)
            merged_servers.append(s)
            added_count += 1

    print(f"[+] Merged: {len(existing_servers)} existing + {added_count} new unique servers = {len(merged_servers)} total servers.")

    # Write merged list back to destination
    merged_content = "\n".join(merged_servers)
    merged_b64 = base64.b64encode(merged_content.encode("utf-8")).decode("utf-8")

    # Make sure target directory exists
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(merged_b64)
    print(f"[+] Successfully wrote merged base64 to {dest_file}")

if __name__ == "__main__":
    main()
