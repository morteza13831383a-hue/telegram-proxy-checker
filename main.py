import os
import time
import requests
import socket
from supabase import create_client, Client

# سورس‌های معتبر و محبوب گیت‌هاب
SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/mrmoein/MTProto-Proxy-List/main/proxies.txt"
]

def check_proxy_connection(ip, port):
    """تست سریع اتصال با تایم‌اوت کوتاه"""
    try:
        start_time = time.time()
        with socket.create_connection((ip, int(port)), timeout=2.0):
            ping = int((time.time() - start_time) * 1000)
            return True, ping
    except:
        return False, 0

def main():
    print("🚀 Starting proxy checker...")
    
    # بررسی اتصال به سوپابیس
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            print("❌ Error: SUPABASE_URL or SUPABASE_KEY is missing in GitHub Secrets!")
            return
            
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"❌ Supabase Connection Error: {e}")
        return

    valid_proxies = []
    
    for source in SOURCES:
        print(f"\n📡 Fetching from {source}...")
        try:
            response = requests.get(source, timeout=10)
            lines = response.text.splitlines()
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
                    
                    is_alive, ping = check_proxy_connection(ip, port)
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
                        print(f"✅ Found Active: {ip}:{port} ({ping}ms)")
                        
                        if count >= 10:  # محدودیت ۱۰ پروکسی از هر سورس برای اجرای سریع
                            break
        except Exception as e:
            print(f"⚠️ Failed to process source {source}: {e}")

    if valid_proxies:
        try:
            print("\n💾 Saving to database...")
            # پاک کردن دیتای قبلی
            supabase.table("proxies").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            # ثبت دیتای جدید
            supabase.table("proxies").insert(valid_proxies).execute()
            print(f"🎉 Success! {len(valid_proxies)} proxies inserted.")
        except Exception as e:
            print(f"❌ Database Insertion Error: {e}")
    else:
        print("\n⚠️ No active proxies found at this time.")

if __name__ == "__main__":
    main()
