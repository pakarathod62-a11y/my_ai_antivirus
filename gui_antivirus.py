import os
import time
import math
import hashlib
import shutil
import psutil
import joblib
import pandas as pd

QUARANTINE_DIR = os.path.expanduser("~/my_ai_antivirus/.quarantine")
if not os.path.exists(QUARANTINE_DIR):
    os.makedirs(QUARANTINE_DIR)

KNOWN_VIRUS_HASHES = [
    "131f95c51ed99360015e3115664166b0fe6964144482393d46c2e8cb4412e0ad",
    "44d88612fea8a8f36de82e1278abb02f",
    "69630e4574ec6798239b091cda43dca0"
]

try:
    model = joblib.load("antivirus_ai_model.pkl")
    MODEL_LOADED = True
except Exception:
    MODEL_LOADED = False

def calculate_hashes(file_path):
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            sha256.update(content)
            md5.update(content)
        return sha256.hexdigest(), md5.hexdigest(), content
    except Exception:
        return "", "", b""

def calculate_entropy(data):
    if not data:
        return 0.0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def quarantine_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(QUARANTINE_DIR, file_name)
        os.chmod(file_path, 0o000)
        shutil.move(file_path, dest_path)
        print(f"[🔒 QUARANTINED] Threat isolated to vault: {file_name}")
    except Exception as e:
        print(f"[-] Quarantine Failed: {e}")

def inspect_file(file_path):
    sha256_hash, md5_hash, content = calculate_hashes(file_path)
    if not content and not sha256_hash:
        return False

    entropy = calculate_entropy(content)
    try:
        file_size = os.path.getsize(file_path)
    except Exception:
        file_size = 0

    is_threat = False
    file_name = os.path.basename(file_path)

    if b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in content:
        print(f"[🚨 CRITICAL THREAT] {file_name} -> EICAR Test Signature!")
        is_threat = True
    elif sha256_hash in KNOWN_VIRUS_HASHES or md5_hash in KNOWN_VIRUS_HASHES:
        print(f"[🚨 CRITICAL THREAT] {file_name} -> Hash Match!")
        is_threat = True
    elif MODEL_LOADED:
        features = pd.DataFrame([{'feature1': file_size, 'feature2': entropy, 'feature3': 0, 'feature4': 0, 'feature5': 0}])
        prediction = model.predict(features)
        if prediction[0] == 1 or entropy > 7.2:
            print(f"[⚠️ SUSPICIOUS] {file_name} -> AI Flagged / High Entropy ({round(entropy,2)})")
            is_threat = True

    return is_threat

def run_deep_scan():
    target_dir = os.path.expanduser("~/Downloads")
    print(f"\n🔍 [DEEP SCAN STARTED] Scanning directory: {target_dir}")
    scanned = 0
    threats = 0
    for root, dirs, files in os.walk(target_dir):
        if ".quarantine" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            scanned += 1
            if inspect_file(file_path):
                quarantine_file(file_path)
                threats += 1
    print(f"\n✅ [SCAN COMPLETE] Scanned: {scanned} files | Threats Quarantined: {threats}\n")

if __name__ == "__main__":
    print("="*50)
    print("🛡️ AI-POWERED HYBRID ANTIVIRUS (CLI MODE)")
    print("="*50)
    print(f"AI Model Status: {'Loaded Successfully!' if MODEL_LOADED else 'Not Loaded'}")
    print("\nRunning Deep Scan on Downloads folder...")
    run_deep_scan()
