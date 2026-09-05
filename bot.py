from flask import Flask
import threading
import requests
import time
import os

# --- KİMLİK BİLGİLERİNİZ ---
TELEGRAM_TOKEN = "8961289480:AAGkJuj82EDaku0AgSf-QHD8sP7GN-BJxGw"
CHAT_ID = "6536751405"
RAPIDAPI_KEY = "b1166aa376msh6bce9e879f341fap13095cjsne913c3d3cb18"
# ---------------------------

app = Flask(__name__)

# Seçkin Lig Havuzu (23 Lig)
SECILI_LIGLER = [
    203, 204, 205, 206, 39, 40, 140, 135, 136, 144, 
    218, 179, 207, 210, 333, 103, 62, 61, 78, 79, 307, 94, 88
]

@app.route('/')
def home():
    return "Yüksek Olasılıklı Profesyonel Bahis Botu Aktif!"

def telegram_mesaj_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram mesaj hatasi:", e)

def canli_maclari_kontrol_et():
    print("Secili ligler yuksek olasilik filtreleriyle taranıyor...")
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
            if lig_id not in SECILI_LIGLER:
                continue
                
            dakika = mac["fixture"]["status"]["elapsed"]
            ev_sahibi = mac["teams"]["home"]["name"]
            deplasman = mac["teams"]["away"]["name"]
            skor_ev = mac["goals"]["home"]
            skor_dep = mac["goals"]["away"]
            
            if dakika is not None:
                # --- İLK YARI YÜKSEK OLASILIKLI SENARYOLARI ---
                # İY 0.5 Üst / İY Ev veya Deplasman Gol / İY KG Var (Dakika 30-41 arası, henüz gol yoksa veya 0-0/1-0 ise)
                if 30 <= dakika <= 41:
                    if skor_ev == 0 and skor_dep == 0:
                        mesaj = f"⚡ <b>İLK YARI YÜKSEK POTANSİYEL</b> ⚡\n\n⚽ {ev_sahibi} 0 - 0 {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: Baskı yoğun! <b>İLK YARI 0,5 ÜST</b> veya <b>İLK YARI GOL VAR</b> olasılığı yüksek.</i>"
                        telegram_mesaj_gonder(mesaj)
                    elif skor_ev > 0 and skor_dep == 0:
                        mesaj = f"⚡ <b>İLK YARI GOL DEVAM SİNYALİ</b> ⚡\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: Ev sahibi baskıda. <b>İLK YARI EV SAHİBİ GOLÜ</b> veya <b>1,5 ÜST</b> değerlendirilebilir.</i>"
                        telegram_mesaj_gonder(mesaj)
                    elif skor_ev == 0 and skor_dep > 0:
                        mesaj = f"⚡ <b>İLK YARI GOL DEVAM SİNYALİ</b> ⚡\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: Deplasman etkili! <b>İLK YARI DEPLASMAN GOLÜ</b> veya <b>KARŞILIKLI GOL VAR</b> yakın.</i>"
                        telegram_mesaj_gonder(mesaj)

                # --- İKİNCİ YARI YÜKSEK OLASILIKLI SENARYOLARI ---
                # Maçı Çevirir / İkinci Yarı 0,5 - 1,5 Üst ve KG Var (Dakika 55-70 arası tek fark veya beraberlik)
                elif 55 <= dakika <= 70:
                    if abs(skor_ev - skor_dep) == 1:
                        geride_olan = ev_sahibi if skor_ev < skor_dep else deplasman
                        mesaj = f"🔄 <b>İKİNCİ YARI REAKSİYON FİLTRESİ</b> 🔄\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: {geride_olan} yükleniyor. <b>İKİNCİ YARI 0,5 ÜST</b>, <b>KG VAR</b> veya <b>MAÇI ÇEVİRİR</b> potansiyeli!</i>"
                        telegram_mesaj_gonder(mesaj)

                # Son Bölüm Baskısı: İkinci Yarı 1.5 Üst, 2.5 Üst, Korner ve Kart Sinyalleri (Dakika 75-87 arası)
                elif 75 <= dakika <= 87:
                    if skor_ev == skor_dep:
                        mesaj = f"🚨 <b>KRİTİK SON DAKİKA FIRSATI</b> 🚨\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: Skor berabere! <b>İKİNCİ YARI 1,5 ÜST</b> / <b>2,5 ÜST</b>, Korner Üst ve Sertlik (Kart) ihtimali dorukta.</i>"
                        telegram_mesaj_gonder(mesaj)
                    elif abs(skor_ev - skor_dep) >= 1:
                        mesaj = f"🚨 <b>BASKI VE KORNER / KART DALGASI</b> 🚨\n\n⚽ {ev_sahibi} {skor_ev} - {skor_dep} {deplasman}\n⏱️ Dakika: {dakika}\n💡 <i>Analiz: Skor değişim aralığı. <b>İKİNCİ YARI 2,5 / 3,5 ÜST</b> veya Son Bölüm Korner/Kart tetiklendi.</i>"
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
    # TEST MESAJI
telegram_mesaj_gonder("🔔 <b>TEST MESAJI:</b> Botumuz başarıyla çalışıyor ve bağlantı kuruldu!")

    threading.Thread(target=bot_dongusu).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
