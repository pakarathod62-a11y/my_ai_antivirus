import os
import time
import math
import hashlib
import shutil
import threading
import psutil
import joblib
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION & PATHS ---
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
    print("[+] AI मॉडल सफलतापूर्वक लोड हो गया!")
except Exception as e:
    print(f"[-] AI मॉडल लोड करने में त्रुटि: {e}")
    exit()

# --- UTILITY FUNCTIONS ---
def quarantine_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(QUARANTINE_DIR, file_name)
        os.chmod(file_path, 000)
        shutil.move(file_path, dest_path)
        print(f"   [🔒 QUARANTINE ACTION] खतरा सुरक्षित रूप से लॉक किया गया: {dest_path}")
    except Exception as e:
        print(f"   [-] Quarantine त्रुटि: {e}")

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

def inspect_file(file_path):
    """फाइल को स्कैन करके खतरे का पता लगाने का कॉमन फंक्शन"""
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
        print(f"\n[🚨 THREAT DETECTED] '{file_name}' (EICAR Test Signature Found)")
        is_threat = True
    elif sha256_hash in KNOWN_VIRUS_HASHES or md5_hash in KNOWN_VIRUS_HASHES:
        print(f"\n[🚨 THREAT DETECTED] '{file_name}' (Blacklisted Hash Match)")
        is_threat = True
    else:
        features = pd.DataFrame([{
            'feature1': file_size, 'feature2': entropy,
            'feature3': 0, 'feature4': 0, 'feature5': 0
        }])
        prediction = model.predict(features)
        if prediction[0] == 1 or entropy > 7.2:
            print(f"\n[⚠️ THREAT DETECTED] '{file_name}' (AI / High Entropy Flag)")
            is_threat = True

    return is_threat

# --- STAGE A: EXISTING FILES DEEP SCAN ---
def run_initial_deep_scan(target_dir):
    print("\n==================================================")
    print(f"🔍 [PHASE 1] पुरानी फाइलों की दीप स्कैनिंग शुरू हो रही है...")
    print(f"📁 फोल्डर: {target_dir}")
    print("==================================================")
    
    scanned = 0
    threats = 0
    
    for root, dirs, files in os.walk(target_dir):
        if ".quarantine" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            scanned += 1
            print(f"[*] Scanning existing files ({scanned}): {file}...", end="\r")
            
            if inspect_file(file_path):
                threats += 1
                quarantine_file(file_path)
                
    print(f"\n\n✅ [PHASE 1 COMPLETE] स्कैन पूरा हुआ!")
    print(f"📊 कुल पुरानी स्कैन की गई फाइलें: {scanned}")
    print(f"🔒 सुरक्षित रूप से क्वारंटाइन की गई फाइलें: {threats}\n")

# --- STAGE B: REAL-TIME WATCHER FOR NEW FILES ---
class FileSecurityHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        print(f"\n[🔔 REAL-TIME FILE ALERT] नई फाइल मिली: {os.path.basename(file_path)}")
        time.sleep(1)
        
        if os.path.exists(file_path):
            if inspect_file(file_path):
                quarantine_file(file_path)
            else:
                print(f"[✅ SAFE] '{os.path.basename(file_path)}' सुरक्षित फाइल है।")

# --- STAGE C: NETWORK MONITORING ---
def continuous_network_monitor():
    while True:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    connections = proc.connections(kind='inet')
                    for conn in connections:
                        if conn.status == 'ESTABLISHED':
                            remote_ip = conn.raddr.ip if conn.raddr else "Unknown"
                            remote_port = conn.raddr.port if conn.raddr else "Unknown"
                            proc_name = proc.info['name'].lower()
                            if proc_name not in ['chrome', 'firefox', 'code', 'systemd']:
                                print(f"\n[🌐 NET TRACKER] सक्रिय कनेक्शन: {proc.info['name']} -> {remote_ip}:{remote_port}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        time.sleep(10)

# --- MASTER MAIN EXECUTION ---
if __name__ == "__main__":
    watch_folder = os.path.expanduser("~/Downloads")
    
    # 1. सबसे पहले पुरानी फाइलों का स्कैन रन करें
    run_initial_deep_scan(watch_folder)
    
    # 2. इसके बाद रियल-टाइम प्रोटेक्शन (Network + File Watcher) शुरू करें
    print("==================================================")
    print("🛡️ [PHASE 2] REAL-TIME PROTECTION & NETWORK IDS ACTIVE")
    print(f"👁️ मॉनिटरिंग फोल्डर: {watch_folder}")
    print(f"🔒 क्वारंटाइन वैल्ट: {QUARANTINE_DIR}")
    print("बंद करने के लिए Ctrl + C दबाएं")
    print("==================================================\n")
    
    # Background Network Monitor
    net_thread = threading.Thread(target=continuous_network_monitor, daemon=True)
    net_thread.start()
    
    # Real-Time File Watcher
    event_handler = FileSecurityHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[-] सुरक्षा सिस्टम सफलतापूर्वक बंद किया गया।")
    observer.join()
