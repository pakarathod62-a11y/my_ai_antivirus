import os
import time
import math
import hashlib
import joblib
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Known EICAR Hashes (MD5 & SHA256)
KNOWN_VIRUS_HASHES = [
    "131f95c51ed99360015e3115664166b0fe6964144482393d46c2e8cb4412e0ad",
    "44d88612fea8a8f36de82e1278abb02f", # MD5
    "69630e4574ec6798239b091cda43dca0"
]

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

try:
    model = joblib.load("antivirus_ai_model.pkl")
    print("[+] AI मॉडल सफलतापूर्वक लोड हो गया!")
except Exception as e:
    print(f"[-] मॉडल लोड नहीं हो सका: {e}")
    exit()

class EnhancedHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        print(f"\n[🔔 NEW FILE] नई फाइल मिली: {os.path.basename(file_path)}")
        print("[*] Multi-Layer Security Scanning चालू हो रहा है...")
        
        time.sleep(1)
        
        if os.path.exists(file_path):
            sha256_hash, md5_hash, content = calculate_hashes(file_path)
            entropy = calculate_entropy(content)
            file_size = os.path.getsize(file_path)
            
            # Layer 1: Signature Search (Direct Text Check for EICAR)
            if b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in content:
                print(f"[🚨 CRITICAL ALERT] Test Virus Found! '{os.path.basename(file_path)}' में EICAR वायरस कोड मौजूद है!")
                return

            # Layer 2: Known Threat Hash Matching
            if sha256_hash in KNOWN_VIRUS_HASHES or md5_hash in KNOWN_VIRUS_HASHES:
                print(f"[🚨 CRITICAL ALERT] Known Threat! '{os.path.basename(file_path)}' का Hash ब्लैकलिस से मैच हुआ है!")
                return

            # Layer 3: AI Model Prediction
            features = pd.DataFrame([{
                'feature1': file_size,
                'feature2': entropy,
                'feature3': 0,
                'feature4': 0,
                'feature5': 0
            }])
            
            prediction = model.predict(features)
            
            if prediction[0] == 1 or entropy > 7.0:
                print(f"[⚠️ ALERT] AI Analysis: '{os.path.basename(file_path)}' एक मैलवेयर/संदिग्ध फाइल है!")
            else:
                print(f"[✅ SAFE] '{os.path.basename(file_path)}' सुरक्षित फाइल है।")

if __name__ == "__main__":
    watch_folder = os.path.expanduser("~/Downloads")
    event_handler = EnhancedHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=False)
    
    print("==================================================")
    print("🛡️ Real-Time Auto-Scanner V2 (Multi-Layer Protection)")
    print(f"👁️ मॉनिटरिंग फोल्डर: {watch_folder}")
    print("बंद करने के लिए Ctrl + C दबाएं")
    print("==================================================")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[-] स्कैनर बंद किया गया।")
    observer.join()
