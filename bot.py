from flask import Flask
import threading
import requests
import time
import os

# --- BURAYA KENDI BILGILERINIZI YAZACAKSINIZ ---
TELEGRAM_TOKEN = "8961289480:AAGkJuj82EDaku0AgSf-QHD8sP7GN-BJxGw"
CHAT_ID = "6536751405"
RAPIDAPI_KEY = "b1166aa376msh6bce9e879f341fap13095cjsne913c3d3cb18"
# ---------------------------------------------

app = Flask(__name__)

# Sizin belirlediğiniz liglerin API-Football ID listesi
SECILI_LIGLER = [
    203,  # Türkiye Süper Lig
    204,  # Türkiye 1. Lig (Trendyol 1. Lig)
    205,  # Türkiye 2. Lig (Nesine 2. Lig)
    206,  # Türkiye 3. Lig (Nesine 3. Lig)
    39,   # İngiltere Premier Lig
    40,   # İngiltere Championship
    140,  # İspanya La Liga
    135,  # İtalya Serie A
    136,  # İtalya Serie B
    144,  # Belçika Pro League
    218,  # Avusturya Bundesliga
    179,  # İskoçya Premiership
    207,  # İsviçre Super League
    210,  # Hırvatistan HNL
    333,  # Ukrayna Premier Ligi
    103,  # Norveç Eliteserien
    62,   # Fransa Ligue 2
    61,   # Fransa Ligue 1
    78,   # Almanya Bundesliga
    79,   # Almanya 2. Bundesliga
    307,  # Suudi Arabistan Pro League
    94,   # Portekiz Primeira Liga
    88    # Hollanda Eredivisie
]

@app.route('/')
def home():
    return "Bot 7/24 Seçili Ligleri ve Analizleri Tarıyor!"

def telegram_mesaj_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram mesaj hatasi:", e)

def canli_maclari_kontrol_et():
    print("Secili ligler ve canli maclar taraniyor...")
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"live": "all"}
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        for mac in data.get("response", []):
            lig_id = mac["league"]["id"]
            
            # Sadece bizim listedeki ligleri incele
            if lig_id not in SECILI_LIGLER:
                continue
                
            dakika = mac["fixture"]["status"]["elapsed"]
            ev_sahibi = mac["teams"]["home"]["name"]
            deplasman = mac["teams"]["away"]["name"]
            skor_ev = mac["goals"]["home"]
            skor_dep = mac["goals"]["away"]
            
            if dakika is not None:
                # Senaryo 1: Beraberlik ve Son 10-15 dakika (Gol / Baskı potansiyeli)
                if 75 <= dakika <= 88 and skor_ev == skor_dep:
                    mesaj = f"🚨 <b>CANLI GOL / BASKI FIRSATI</b> 🚨\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: Beraberlik bozulabilir, son dakika baskısı yüksek!</i>"
                    telegram_mesaj_gonder(mesaj)
                    
                # Senaryo 2: Deplasman veya Ev Sahibi geride, maç kopabilir / KG dönebilir (Örn: Tek farkla geride olma durumu)
                elif 65 <= dakika <= 85 and abs(skor_ev - skor_dep) == 1:
                    geride_olan = ev_sahibi if skor_ev < skor_dep else deplasman
                    mesaj = f"🚨 <b>MAÇI ÇEVİRİR / KG FIRSATI</b> 🚨\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: {geride_olan} geride bastırıyor, KG veya Maç Çevirir potansiyeli!</i>"
                    telegram_mesaj_gonder(mesaj)
                
    except Exception as e:
        print("API Veri cekilirken hata:", e)

def bot_dongusu():
    while True:
        try:
            canli_maclari_kontrol_et()
        except Exception as e:
            print("Dongu hatasi:", e)
        time.sleep(900)

if __name__ == "__main__":
    threading.Thread(target=bot_dongusu).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
