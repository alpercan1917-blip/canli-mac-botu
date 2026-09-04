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

@app.route('/')
def home():
    return "Bot 7/24 Aktif ve Maclari Tariyor!"

def telegram_mesaj_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram mesaj hatasi:", e)

def canli_maclari_kontrol_et():
    print("Canli maclar taraniyor...")
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
            dakika = mac["fixture"]["status"]["elapsed"]
            ev_sahibi = mac["teams"]["home"]["name"]
            deplasman = mac["teams"]["away"]["name"]
            skor_ev = mac["goals"]["home"]
            skor_dep = mac["goals"]["away"]
            
            if dakika is not None and 75 <= dakika <= 85 and skor_ev == skor_dep:
                mesaj = f"🚨 <b>CANLI FIRSAT Yakalandi</b> 🚨\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 Analiz: Son 10 dakika baskisi, risk alinabilir!"
                telegram_mesaj_gonder(mesaj)
                print(f"Bildirim gonderildi: {ev_sahibi} vs {deplasman}")
                
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
