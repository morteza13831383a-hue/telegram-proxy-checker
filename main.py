import os
import socket
import time
import urllib.request
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing in environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# منابع معتبر و پایدار پروکسی تلگرام
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/Hookeai/MTProtoProxy/main/MTProtoProxy.txt"
]

def check_tcp_proxy(ip, port, timeout=3.0):
    """تست سریع اتصال TCP پورت پروکسی"""
    start_time = time.time()
    try:
        with socket.create_connection((ip, int(port)), timeout=timeout):
            ping = int((time.time() - start_time) * 1000)
            return True, ping
    except Exception:
        return False, 0

def fetch_and_parse_proxies():
    """استخراج و جداسازی امن پروکسی‌ها"""
    valid_proxies = []
    
    for source in PROXY_SOURCES:
        try:
            req = urllib.request.Request(
                source, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                lines = response.read().decode('utf-8', errors='ignore').splitlines()
                count = 0
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) >= 2:
                        ip = parts[0].strip()
                        port_str = parts[1].strip()
                        
                        if not port_str.isdigit():
                            continue
                        
                        port = int(port_str)
                        secret = parts[2].strip() if len(parts) > 2 else ""
                        protocol = "MTProto" if secret else "SOCKS5"
                        
                        # تست سلامت اتصال قبل از ثبت
                        is_alive, ping = check_tcp_proxy(ip, port)
                        if is_alive:
                            valid_proxies.append({
                                "ip": ip,
                                "port": port,
                                "secret": secret,
                                "protocol": protocol,
                                "country_code": "US",
                                "ping": ping,
                                "is_active": True
                            })
                            count += 1
                            print(f"✅ Valid: {ip}:{port} ({protocol}) - Ping: {ping}ms")
                            
                            # محدودیت تعداد برای هر سورس جهت سرعت اجرا
                            if count >= 15:
                                break
        except Exception as e:
            print(f"⚠️ Error fetching source {source}: {e}")
            
    return valid_proxies

def main():
    print("🚀 Starting proxy collection and check...")
    verified_proxies = fetch_and_parse_proxies()
    
    if verified_proxies:
        try:
            # پاک کردن رکوردهای قدیمی برای جلوگیری از انباشتگی
            supabase.table("proxies").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            
            # درج دسته‌ای پروکسی‌های جدید و سالم
            response = supabase.table("proxies").insert(verified_proxies).execute()
            print(f"🎉 Successfully inserted {len(verified_proxies)} proxies into Supabase!")
        except Exception as db_err:
            print(f"❌ Database error: {db_err}")
            raise db_err
    else:
        print("⚠️ No active proxies found in this run.")

if __name__ == "__main__":
    main()
