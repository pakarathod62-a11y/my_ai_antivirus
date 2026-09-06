import os
import time
import math
import joblib
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 1. Entropy कैलकुलेट करने का फंक्शन
def calculate_entropy(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        if not data:
            return 0.0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy
    except Exception:
        return 0.0

# 2. AI मॉडल लोड करें
try:
    model = joblib.load("antivirus_ai_model.pkl")
    print("[+] AI मॉडल लोड हो गया!")
except Exception as e:
    print(f"[-] मॉडल लोड नहीं हो सका: {e}")
    exit()

# 3. नई फाइल आने पर ऑटो-स्कैन करने की लॉजिक
class DownloadFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        # अगर कोई फोल्डर बना है तो उसे इग्नोर करें
        if event.is_directory:
            return
        
        file_path = event.src_path
        print(f"\n[🔔 NEW FILE] नई फाइल मिली: {os.path.basename(file_path)}")
        print("[*] ऑटोमैटिक AI स्कैन चालू हो रहा है...")
        
        # फाइल डाउनलोड पूरी होने के लिए 1 सेकंड रुकें
        time.sleep(1)
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            entropy = calculate_entropy(file_path)
            
            features = pd.DataFrame([{
                'feature1': file_size,
                'feature2': entropy,
                'feature3': 0,
                'feature4': 0,
                'feature5': 0
            }])
            
            prediction = model.predict(features)
            
            if prediction[0] == 1:
                print(f"[⚠️ ALERT] खतरा मिला! '{os.path.basename(file_path)}' एक संदिग्ध/मैलवेयर फाइल है!")
            else:
                print(f"[✅ SAFE] '{os.path.basename(file_path)}' सुरक्षित फाइल है।")

# 4. वॉचडॉग चालू करना
if __name__ == "__main__":
    # जिस फोल्डर पर नज़र रखनी है (अभी हम Downloads फोल्डर सेट कर रहे हैं)
    watch_folder = os.path.expanduser("~/Downloads")
    
    event_handler = DownloadFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_folder, recursive=False)
    
    print("==================================================")
    print(f"🛡️ Real-Time Auto-Scanner Active!")
    print(f"👁️ नज़र रखी जा रही है: {watch_folder}")
    print("बंद करने के लिए Ctrl + C दबाएं")
    print("==================================================")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[-] ऑटो-स्कैनर बंद कर दिया गया।")
    observer.join()
