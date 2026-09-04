from flask import Flask
import threading
import requests
import time
import os

# --- BURAYA KENDÝ BÝLGÝLERÝNÝZÝ YAZACAKSINIZ ---
TELEGRAM_TOKEN = "BURAYA_BOTFATHER_TOKENI_YAZ"
CHAT_ID = "BURAYA_USERINFOBOT_ID_YAZ"
RAPIDAPI_KEY = "BURAYA_RAPIDAPI_ANAHTARI_YAZ"
# ---------------------------------------------

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot 7/24 Aktif ve Maçlarý Tarýyor!"

def telegram_mesaj_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram mesaj hatasý:", e)

def canli_maclari_kontrol_et():
    print("Canlý maçlar taranýyor...")
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"live": "all"}
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        # Maçlarý tek tek inceleyelim
        for mac in data.get("response", []):
            dakika = mac["fixture"]["status"]["elapsed"]
            ev_sahibi = mac["teams"]["home"]["name"]
            deplasman = mac["teams"]["away"]["name"]
            skor_ev = mac["goals"]["home"]
            skor_dep = mac["goals"]["away"]
            
            # ALGORÝTMA: Maç 75 ile 85. dakika arasýndaysa ve skor berabere ise
            if dakika is not None and 75 <= dakika <= 85 and skor_ev == skor_dep:
                mesaj = f"?? <b>CANLI FIRSAT Yakalandý</b> ??\n\n? {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n?? Dakika: {dakika}\n?? Analiz: Son 10 dakika baskýsý, risk alýnabilir!"
                telegram_mesaj_gonder(mesaj)
                print(f"Bildirim gönderildi: {ev_sahibi} vs {deplasman}")
                
    except Exception as e:
        print("API Veri çekilirken hata:", e)

def bot_dongusu():
    while True:
        try:
            canli_maclari_kontrol_et()
        except Exception as e:
            print("Döngü hatasý:", e)
        time.sleep(900) # 15 dakikada bir tarar

if __name__ == "__main__":
    threading.Thread(target=bot_dongusu).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)