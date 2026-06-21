import base64
import os
import re
import shutil

SUPPORTED_SCHEMES=("vmess","vless","trojan","trojan-go","ss","hysteria2","hy2")
LINK_RE=re.compile(r'(?i)\b(?:'+'|'.join(re.escape(s) for s in SUPPORTED_SCHEMES)+r')://[^\s<>"\']+')

def b64d(s):
    s=s.strip().replace('\n','').replace(' ','')
    for decoder in (base64.b64decode, base64.urlsafe_b64decode):
        for pad in ("", "=", "=="):
            try:
                return decoder(s + pad).decode('utf-8', errors='ignore')
            except:
                pass
    return ""

def extract_links(txt):
    return [line.strip() for line in LINK_RE.findall(txt or "") if line.strip()]

def decode_subscription(raw):
    raw=(raw or "").strip()
    if not raw:
        return []
    decoded=b64d(raw)
    if "://" in decoded:
        return extract_links(decoded)
    return extract_links(raw)

def encode_subscription(servers):
    return base64.b64encode("\n".join(servers).encode("utf-8")).decode("utf-8")

def read_subscription(path, label):
    if not os.path.exists(path):
        print(f"[!] {label} file not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw=f.read()
    servers=decode_subscription(raw)
    print(f"[+] Loaded {len(servers)} servers from {label}: {path}")
    return servers

def atomic_write(path, content):
    directory=os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp=path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)

def main():
    new_file=os.environ.get("NEW_SUB_FILE", "clean_sub.txt")
    dest_file=os.environ.get("DEST_SUB_FILE", os.path.join("public_repo", "clean_sub.txt"))
    create_backup=os.environ.get("CREATE_BACKUP", "1") != "0"

    new_servers=read_subscription(new_file, "new")
    if not new_servers:
        print("[-] No new servers found. Destination clean_sub.txt was not changed.")
        return

    existing_servers=read_subscription(dest_file, "existing")
    seen=set(existing_servers)
    added=[]
    for server in new_servers:
        if server not in seen:
            seen.add(server)
            added.append(server)

    if not added:
        print(f"[-] No new unique servers. Destination already contains all {len(new_servers)} checked servers.")
        return

    merged=existing_servers + added
    if create_backup and os.path.exists(dest_file):
        shutil.copy2(dest_file, dest_file + ".bak")
        print(f"[+] Backup saved to {dest_file}.bak")

    merged_b64=encode_subscription(merged)
    atomic_write(dest_file, merged_b64)
    print(f"[+] Appended {len(added)} new unique servers to {dest_file}")
    print(f"[+] Destination total: {len(merged)} servers")

if __name__ == "__main__":
    main()
