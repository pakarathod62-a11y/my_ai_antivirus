import os
import joblib
import pandas as pd

print("[+] AI मॉडल लोड हो रहा है...")
model = joblib.load("antivirus_ai_model.pkl")
print("[+] AI मॉडल सफलतापूर्वक लोड हो गया!")

target = input("स्कैन करने के लिए फाइल का पाथ दर्ज करें: ")

if os.path.exists(target):
    file_size = os.path.getsize(target)
    # 5 फीचर्स का डेटा फ्रेम
    features = pd.DataFrame([{
        'feature1': file_size,
        'feature2': 0,
        'feature3': 0,
        'feature4': 0,
        'feature5': 0
    }])

    prediction = model.predict(features)
    if prediction[0] == 1:
        print(f"[ALERT] खतरा मिला! '{target}' एक मैलवेयर फाइल है।")
    else:
        print(f"[SAFE] '{target}' एक सुरक्षित फाइल है।")
else:
    print("[-] दी गई फाइल मौजूद नहीं है!")
