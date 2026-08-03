import json
import time
import requests
import socket

# سورس‌های معتبر پروکسی
SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/mrmoein/MTProto-Proxy-List/main/proxies.txt"
]

def check_proxy_connection(ip, port):
    try:
        start_time = time.time()
        with socket.create_connection((ip, int(port)), timeout=2.0):
            ping = int((time.time() - start_time) * 1000)
            return True, ping
    except:
        return False, 0

def main():
    print("🚀 Starting proxy checker (No-DB Version)...")
    valid_proxies = []
    
    for source in SOURCES:
        try:
            response = requests.get(source, timeout=10)
            lines = response.text.splitlines()
            count = 0
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                parts = line.split(':')
                if len(parts) >= 2:
                    ip = parts[0].strip()
                    port_str = parts[1].strip()
                    if not port_str.isdigit(): continue
                        
                    port = int(port_str)
                    secret = parts[2].strip() if len(parts) > 2 else ""
                    protocol = "MTProto" if secret else "SOCKS5"
                    
                    is_alive, ping = check_proxy_connection(ip, port)
                    if is_alive:
                        valid_proxies.append({
                            "ip": ip, "port": port, "secret": secret,
                            "protocol": protocol, "country_code": "US", "ping": ping
                        })
                        count += 1
                        print(f"✅ Found: {ip}:{port} ({ping}ms)")
                        if count >= 15: # گرفتن ۱۵ پروکسی از هر سورس (جمعا ۳۰ تا)
                            break
        except Exception as e:
            print(f"⚠️ Error on {source}: {e}")

    # ذخیره به صورت فایل JSON در خود گیت‌هاب
    if valid_proxies:
        with open("proxies.json", "w", encoding="utf-8") as f:
            json.dump(valid_proxies, f, indent=4)
        print(f"🎉 Saved {len(valid_proxies)} proxies to proxies.json!")
    else:
        # اگر پروکسی پیدا نشد، یک لیست خالی ذخیره می‌کنیم تا سایت کرش نکنه
        with open("proxies.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        print("⚠️ No active proxies found. Saved empty list.")

if __name__ == "__main__":
    main()
