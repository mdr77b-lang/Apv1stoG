import os
import shutil
import base64
import subprocess

def test():
    # Setup test workspace
    test_dir = "test_env"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Copy merge_sub.py to test_env
    shutil.copy("merge_sub.py", os.path.join(test_dir, "merge_sub.py"))
    
    os.chdir(test_dir)
    
    # 1. Test case: destination file doesn't exist yet
    new_servers = ["vmess://server1", "vmess://server2"]
    new_b64 = base64.b64encode("\n".join(new_servers).encode("utf-8")).decode("utf-8")
    with open("clean_sub.txt", "w") as f:
        f.write(new_b64)
        
    print("Running merge with missing destination...")
    subprocess.run(["python", "merge_sub.py"])
    
    # Verify result
    with open("public_repo/clean_sub.txt", "r") as f:
        res_b64 = f.read().strip()
    res_content = base64.b64decode(res_b64).decode("utf-8")
    res_servers = res_content.splitlines()
    print("Result 1:", res_servers)
    assert res_servers == ["vmess://server1", "vmess://server2"]
    
    # 2. Test case: destination exists, merges and deduplicates
    existing_servers = ["vmess://server2", "vmess://server3"]
    existing_b64 = base64.b64encode("\n".join(existing_servers).encode("utf-8")).decode("utf-8")
    os.makedirs("public_repo", exist_ok=True)
    with open("public_repo/clean_sub.txt", "w") as f:
        f.write(existing_b64)
        
    print("Running merge with existing destination...")
    subprocess.run(["python", "merge_sub.py"])
    
    # Verify result
    with open("public_repo/clean_sub.txt", "r") as f:
        res_b64 = f.read().strip()
    res_content = base64.b64decode(res_b64).decode("utf-8")
    res_servers = res_content.splitlines()
    print("Result 2 (merged):", res_servers)
    # vmess://server2 and vmess://server3 should be preserved, and only new vmess://server1 added
    # Since we preserve existing servers first: ["vmess://server2", "vmess://server3", "vmess://server1"]
    assert res_servers == ["vmess://server2", "vmess://server3", "vmess://server1"]
    print("[+] All assertions passed successfully!")
    
    # Cleanup
    os.chdir("..")
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    test()
