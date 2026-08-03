import os
import asyncio
import socket
import time
import urllib.request
import json
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# منابع عمومی دریافت پروکسی
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/Hookeai/MTProtoProxy/main/MTProtoProxy.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"
]

async def check_proxy(ip, port):
    """تست آنلاین بودن و پینگ پروکسی"""
    start_time = time.time()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, int(port)), timeout=3.0
        )
        writer.close()
        await writer.wait_closed()
        ping = int((time.time() - start_time) * 1000)
        return True, ping
    except:
        return False, 0

def fetch_proxies():
    """دریافت لیست پروکسی‌ها از سورس‌ها"""
    proxies = []
    for source in PROXY_SOURCES:
        try:
            req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                lines = response.read().decode('utf-8').splitlines()
                for line in lines[:20]: # دریافت ۲۰ پروکسی برتر از هر سورس
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        ip = parts[0]
                        port = parts[1]
                        secret = parts[2] if len(parts) > 2 else ""
                        protocol = "MTProto" if secret else "SOCKS5"
                        proxies.append({"ip": ip, "port": port, "secret": secret, "protocol": protocol})
        except Exception as e:
            print(f"Error fetching from {source}: {e}")
    return proxies

async def main():
    print("Fetching proxies...")
    raw_proxies = fetch_proxies()
    
    verified_proxies = []
    for p in raw_proxies:
        is_alive, ping = await check_proxy(p['ip'], p['port'])
        if is_alive:
            verified_proxies.append({
                "ip": p['ip'],
                "port": int(p['port']),
                "secret": p['secret'],
                "protocol": p['protocol'],
                "country_code": "US", # به طور پیش‌فرض
                "ping": ping,
                "is_active": True
            })
            print(f"✅ Active Proxy Found: {p['ip']}:{p['port']} - Ping: {ping}ms")

    if verified_proxies:
        # پاکسازی پروکسی‌های قدیمی و غیرفعال
        supabase.table("proxies").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        # درج پروکسی‌های جدید و سالم
        supabase.table("proxies").insert(verified_proxies).execute()
        print(f"Successfully inserted {len(verified_proxies)} proxies into Supabase!")

if __name__ == "__main__":
    asyncio.run(main())
