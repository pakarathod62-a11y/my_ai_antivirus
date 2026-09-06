import psutil
import time

def monitor_network_connections():
    print("\n==================================================")
    print("🌐 Real-Time Process & Network Activity Monitor")
    print("==================================================")
    print("बैकग्राउंड में चल रहे नेटवर्क कनेक्शनों की जांच हो रही है...\n")
    
    suspicious_count = 0
    
    # सिस्टम में चल रहे सभी प्रोसेस और उनके नेटवर्क कनेक्शनों को स्कैन करें
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            connections = proc.connections(kind='inet')
            for conn in connections:
                # अगर कोई प्रोसेस 'ESTABLISHED' स्टेट में इंटरनेट से डेटा ले/दे रहा है
                if conn.status == 'ESTABLISHED':
                    remote_ip = conn.raddr.ip if conn.raddr else "Unknown"
                    remote_port = conn.raddr.port if conn.raddr else "Unknown"
                    
                    # कॉमन ब्राउज़र्स के अलावा अन्य अनजान प्रोसेस को अलर्ट करें
                    is_common_browser = proc.info['name'].lower() in ['chrome', 'firefox', 'browser', 'code']
                    
                    if not is_common_browser:
                        print(f"[⚠️ NETWORK ALERT] प्रोसेस: '{proc.info['name']}' (PID: {proc.info['pid']}) -> Connected to Remote IP: {remote_ip}:{remote_port}")
                        suspicious_count += 1
                    else:
                        print(f"[ℹ️ NORMAL] {proc.info['name']} -> IP: {remote_ip}")
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    if suspicious_count == 0:
        print("\n[✅ SAFE] कोई भी असामान्य बैकग्राउंड नेटवर्क कनेक्शन नहीं मिला।")

if __name__ == "__main__":
    try:
        while True:
            monitor_network_connections()
            print("\n[+] 5 सेकंड बाद दोबारा स्कैन होगा... (बंद करने के लिए Ctrl + C दबाएं)")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[-] नेटवर्क मॉनिटर बंद कर दिया गया।")
