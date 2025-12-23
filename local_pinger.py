# local_pinger.py
import subprocess
import time
import requests
from datetime import datetime

regions = {
"Dar es Salaam": {"wan": "10.8.235.22", "gateway": "10.8.235.21", "lan":  "10.11.0.1"},
    "Temeke": {"wan": "10.8.238.250", "gateway": "10.8.238.249", "lan": "10.8.63.1"},
    "Kinondoni": {"wan": "10.8.234.6", "gateway": "10.8.234.5", "lan": "10.12.2.1"},
    "Upanga": {"wan": "10.8.238.226", "gateway": "10.8.238.225", "lan": "10.12.3.1"},
    "Ilala": {"wan": "10.8.234.2", "gateway": "10.8.234.1", "lan":  "10.12.6.1"},
    "Dodoma": {"wan": "10.20.251.82", "gateway": "10.20.251.81", "lan": "10.20.11.1"},
    "Tabora": {"wan": "10.20.251.206", "gateway": "10.20.251.205", "lan": "10.20.12.1"},
    "Shinyanga": {"wan": "10.20.251.226", "gateway": "10.20.251.225", "lan": "10.20.13.1"},
    "Mwanza": {"wan": "10.20.254.226", "gateway": "10.20.254.225", "lan": "10.20.63.1"},
    "Iringa": {"wan": "10.20.251.42", "gateway": "10.20.251.41", "lan": "10.24.75.1"},
    "Kigoma": {"wan": "10.20.252.66", "gateway": "10.20.252.65", "lan": "10.4.0.1"},
    "Kagera": {"wan": "10.20.252.70", "gateway": "10.20.252.69", "lan": "10.4.1.1"},
    "Musoma": {"wan": "10.20.252.70", "gateway": "10.20.252.73", "lan": "10.4.2.1"},
    "Singida": {"wan": "10.8.234.6", "gateway": "10.20.248.17", "lan": "10.4.3.1"},
    "Lindi": {"wan": "10.8.238.66", "gateway": "10.8.238.70", "lan": "10.4.4.1"},
    "Mtwara": {"wan": "10.8.238.70", "gateway": "10.20.252.69", "lan":  "10.4.5.1"},
    "Metropolitan": {"wan": "10.8.235.142", "gateway": "10.8.235.141", "lan": "10.4.6.1"},
    "Arusha": {"wan": "10.4.255.150", "gateway": "10.4.255.149", "lan":  "10.4.37.1"},
    "Moshi": {"wan": "10.6.255.106", "gateway": "10.6.255.105", "lan": "10.6.24.1"},
    "Tanga": {"wan": "10.7.255.90", "gateway": "10.7.255.89", "lan": "10.7.21.1"},
    "Morogoro": {"wan": "10.25.79.74", "gateway": "10.25.79.73", "lan": "10.25.86.1"},
    "Mbeya": {"wan": "10.36.254.174", "gateway": "10.36.254.173", "lan": "10.64.166.1"},
    "Katavi": {"wan": "10.35.255.110", "gateway": "10.35.255.109", "lan": "10.64.167.1"},
    "Ruvuma": {"wan": "10.36.249.85", "gateway": "10.36.249.84", "lan": "10.64.168.1"},
    "HQ Internet": {"wan": "41.59.57.102", "gateway": "41.59.57.102","lan": "41.59.57.101"},
    "Dodoma(Mtumba Madini)": {"wan": "10.20.234.150", "gateway": "10.20.234.149", "lan": "10.22.11.1"},
    "Kawe": {"wan": "10.30.45.6", "gateway": "10.30.45.5", "lan": "10.15.1.1"},
    "Urafiki": {"wan": "10.4.249.14", "gateway": "10.4.249.13", "lan": "10.15.2.1"},
    "Morroco Square": {"wan": "10.30.11.2", "gateway": "10.30.11.1", "lan": "10.15.3.1"},
    "NHC House": {"wan": "10.4.244.146", "gateway": "10.4.244.145", "lan": "10.15.4.1"},
}

LOCAL_URL  = "http://localhost:5000/update"      # ← Local Flask
CLOUD_URL  = "https://newcloud.onrender.com/update"
INTERVAL   = 10

def ping_ip(ip):
    try:
        out = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", ip],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5
        )
        return "ACTIVE" if "TTL=" in out.stdout else "INACTIVE"
    except:
        return "INACTIVE"

def collect_results():
    payload = {}
    for region, info in regions.items():
        lan = info["lan"]
        lan_ips = lan if isinstance(lan, list) else [lan]
        rows = [
            {"ip": info["wan"],      "label": "WAN",      "status": ping_ip(info["wan"])},
            {"ip": info["gateway"],  "label": "Gateway",  "status": ping_ip(info["gateway"])},
        ]
        rows += [{"ip": ip, "label": "LAN", "status": ping_ip(ip)} for ip in lan_ips]
        payload[region] = rows
    return payload

def send_to(url):
    try:
        r = requests.post(url, json={"results": collect_results()}, timeout=10)
        if r.status_code == 200:
            print(f"[{datetime.now():%H:%M:%S}] → {url.split('/')[-2]}: OK")
        else:
            print(f"[{datetime.now():%H:%M:%S}] → {url.split('/')[-2]}: HTTP {r.status_code}")
    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] → {url.split('/')[-2]}: ERROR {e}")

if __name__ == "__main__":
    print("Pinger → LOCAL[](http://localhost:5000) + CLOUD (newcloud.onrender.com)")
    while True:
        send_to(LOCAL_URL)
        send_to(CLOUD_URL)
        time.sleep(INTERVAL)