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

# --- 1. SETTINGS & PATHS ---
QUARANTINE_DIR = os.path.expanduser("~/my_ai_antivirus/.quarantine")
if not os.path.exists(QUARANTINE_DIR):
    os.makedirs(QUARANTINE_DIR)

KNOWN_VIRUS_HASHES = [
    "131f95c51ed99360015e3115664166b0fe6964144482393d46c2e8cb4412e0ad",
    "44d88612fea8a8f36de82e1278abb02f",
    "69630e4574ec6798239b091cda43dca0"
]

# AI Model Loading
try:
    model = joblib.load("antivirus_ai_model.pkl")
    print("[+] AI मॉडल सफलतापूर्वक लोड हुआ!")
except Exception as e:
    print(f"[-] AI मॉडल लोड करने में समस्या: {e}")
    exit()

# --- 2. HELPER FUNCTIONS ---
def quarantine_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(QUARANTINE_DIR, file_name)
        os.chmod(file_path, 000)
        shutil.move(file_path, dest_path)
        print(f"\n[🔒 QUARANTINED] फाइल आइसोलेट कर दी गई: {dest_path}")
    except Exception as e:
        print(f"[-] Quarantine त्रुटि: {e}")

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

# --- 3. LAYER A: REAL-TIME FILE SCANNER ---
class QuarantineHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        print(f"\n[🔔 NEW FILE] नई फाइल मिली: {os.path.basename(file_path)}")
        print("[*] 4-Layer Security Analysis चालू है...")
        
        time.sleep(1)
        
        if os.path.exists(file_path):
            sha256_hash, md5_hash, content = calculate_hashes(file_path)
            entropy = calculate_entropy(content)
            file_size = os.path.getsize(file_path)
            
            is_threat = False
            
            if b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in content:
                print(f"[🚨 FILE ALERT] EICAR Test Virus पाया गया!")
                is_threat = True
            elif sha256_hash in KNOWN_VIRUS_HASHES or md5_hash in KNOWN_VIRUS_HASHES:
                print(f"[🚨 FILE ALERT] Known Threat Hash Match!")
                is_threat = True
            else:
                features = pd.DataFrame([{
                    'feature1': file_size, 'feature2': entropy,
                    'feature3': 0, 'feature4': 0, 'feature5': 0
                }])
                prediction = model.predict(features)
                if prediction[0] == 1 or entropy > 7.0:
                    print(f"[⚠️ FILE ALERT] AI Model ने फाइल को संदिग्ध पाया!")
                    is_threat = True

            if is_threat:
                quarantine_file(file_path)
            else:
                print(f"[✅ FILE SAFE] '{os.path.basename(file_path)}' सुरक्षित है।")

# --- 4. LAYER B: LIVE NETWORK & IDS MONITORING ---
def live_network_monitor():
    print("[+] LIVE Network & Intrusion Monitor active in Background...")
    seen_connections = set()
    
    while True:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    connections = proc.connections(kind='inet')
                    for conn in connections:
                        if conn.status == 'ESTABLISHED':
                            remote_ip = conn.raddr.ip if conn.raddr else None
                            remote_port = conn.raddr.port if conn.raddr else None
                            
                            conn_id = (proc.info['pid'], remote_ip, remote_port)
                            
                            if conn_id not in seen_connections:
                                seen_connections.add(conn_id)
                                proc_name = proc.info['name'].lower()
                                
                                # अगर कोई अनजान प्रोसेस संदिग्ध पोर्ट (जैसे 4444, 8888, 6667) पर कनेक्ट हो
                                suspicious_ports = [4444, 8888, 6667, 31337]
                                if remote_port in suspicious_ports:
                                    print(f"\n[🚨 NETWORK INTRUSION ALERT] संभावित रिवर्स-शेल/अटैक डिटेक्ट हुआ!")
                                    print(f"    प्रोसेस: {proc.info['name']} (PID: {proc.info['pid']}) -> IP: {remote_ip}:{remote_port}")
                                else:
                                    # नॉर्मल कनेक्शन ट्रैकिंग
                                    if proc_name not in ['chrome', 'firefox', 'code']:
                                        print(f"\n[🌐 NET MONITOR] नया बैकग्राउंड कनेक्शन: {proc.info['name']} -> {remote_ip}:{remote_port}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        time.sleep(4)

# --- 5. MAIN EXECUTION (MULTI-THREADED) ---
if __name__ == "__main__":
    print("==================================================")
    print("🛡️ COMPLETE AI SECURITY SUITE (ANTIVIRUS + IDS)")
    print("👁️ File Scanner Monitoring: ~/Downloads")
    print("🌐 Network Monitor: Live IP & Connection Tracker")
    print("🔒 Quarantine Vault: Enabled")
    print("बंद करने के लिए Ctrl + C दबाएं")
    print("==================================================")
    
    # 1. Start Network Monitoring in Background Thread
    net_thread = threading.Thread(target=live_network_monitor, daemon=True)
    net_thread.start()
    
    # 2. Start File Watcher in Main Thread
    watch_folder = os.path.expanduser("~/Downloads")
    event_handler = QuarantineHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[-] एंटीवायरस और नेटवर्क सुरक्षा बंद कर दी गई।")
    observer.join()
