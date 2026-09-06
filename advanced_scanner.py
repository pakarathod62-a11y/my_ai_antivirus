import os
import math
import hashlib
import psutil
import joblib
import pandas as pd

# 1. Entropy कैलकुलेट करने का फंक्शन (फाइल के अंदर के पैटर्न/एन्क्रिप्शन की जांच)
def calculate_entropy(file_path):
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

# 2. एडवांस फीचर एक्सट्रैक्शन (Static Analysis)
def extract_advanced_features(file_path):
    file_size = os.path.getsize(file_path)
    entropy = calculate_entropy(file_path)
    
    # 5 फीचर्स: Size, Entropy, और 3 प्लेसहोल्डर्स
    features = pd.DataFrame([{
        'feature1': file_size,
        'feature2': entropy,
        'feature3': 0,
        'feature4': 0,
        'feature5': 0
    }])
    return features, entropy

# 3. बैकग्राउंड प्रोसेस के व्यवहार की जांच (Behavioral Analysis)
def monitor_system_behavior():
    print("\n[📊 Dynamic Behavior Monitor] बैकग्राउंड प्रोसेस की जांच हो रही है...")
    suspicious_found = False
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # अगर कोई प्रोसेस असामान्य रूप से बहुत ज्यादा CPU इस्तेमाल कर रहा है
            if proc.info['cpu_percent'] > 80.0:
                print(f"[⚠️ WARNING] संदिग्ध बर्ताव: {proc.info['name']} (PID: {proc.info['pid']}) अत्यधिक CPU ({proc.info['cpu_percent']}%) इस्तेमाल कर रहा है!")
                suspicious_found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    if not suspicious_found:
        print("[✅ SAFE] बैकग्राउंड में चल रहे सभी प्रोसेस का व्यवहार सामान्य है।")

# --- मुख्य प्रोग्राम ---
if __name__ == "__main__":
    print("========================================")
    print("🛡️ AI Hybrid Antivirus (Static + Behavior)")
    print("========================================")
    
    try:
        model = joblib.load("antivirus_ai_model.pkl")
        print("[+] AI मॉडल सफलतापूर्वक लोड हो गया!")
    except Exception as e:
        print(f"[-] मॉडल लोड नहीं हो सका: {e}")
        exit()

    # फाइल स्कैन (Static)
    target = input("\nस्कैन के लिए फाइल पाथ डालें (या Enter दबाकर Behavior Monitor चलाएं): ")
    
    if target and os.path.exists(target):
        features, entropy_val = extract_advanced_features(target)
        print(f"[*] फाइल Entropy वैल्यू: {entropy_val:.2f} (अत्यधिक रैंडमनेस = संदिग्ध)")
        
        prediction = model.predict(features)
        if prediction[0] == 1:
            print(f"[ALERT] खतरा मिला! '{target}' एक मैलवेयर फाइल है।")
        else:
            print(f"[SAFE] '{target}' एक सुरक्षित फाइल है।")
    else:
        print("[-] कोई फाइल नहीं चुनी गई, केवल सिस्टम मॉनिटरिंग चालू की जा रही है...")

    # बिहेवियर मॉनिटरिंग चलाएं (Dynamic)
    monitor_system_behavior()
