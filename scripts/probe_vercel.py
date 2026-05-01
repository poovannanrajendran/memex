import requests
import time
import sys

def probe_site(url="https://memex-poovi.vercel.app/", max_retries=5, delay=10):
    print(f"Probing Vercel deployment at {url}...")
    
    for i in range(max_retries):
        try:
            # We add a timestamp to bypass any aggressive CDN caching during the probe
            response = requests.get(f"{url}?t={int(time.time())}", timeout=10)
            if response.status_code == 200:
                print(f"✅ Vercel site is LIVE and responding (Status 200)")
                # Search for a unique string that confirms it's Poovi's Second Brain
                if "Poovi's Second Brain" in response.text:
                    print("✅ Verified: Correct content is being served.")
                    return True
                else:
                    print("⚠️  Warning: Site is up but 'Second Brain' string not found.")
            else:
                print(f"⏳ Attempt {i+1}: Site returned status {response.status_code}. Waiting {delay}s...")
        except Exception as e:
            print(f"⏳ Attempt {i+1}: Connection failed ({e}). Waiting {delay}s...")
            
        time.sleep(delay)
        
    print("❌ Probe failed: Site did not respond with success after multiple attempts.")
    return False

if __name__ == "__main__":
    probe_site()
