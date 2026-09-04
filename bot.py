from flask import Flask
import threading
import requests
import time
import os

# Render için göstermelik bir vitrin (web sayfası) oluşturuyoruz
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot 7/24 Aktif ve Maçları Tarıyor!"

# Asıl botunuzun maçları taradığı kısım (Telegram ve RapidAPI bilgilerinizi buraya ekleyeceksiniz)
def canli_maclari_kontrol_et():
    # Önceki versiyondaki API bağlantısı ve Telegram mesaj gönderme kodlarınız buraya gelecek
    print("Maçlar taranıyor...")

def bot_dongusu():
    while True:
        try:
            canli_maclari_kontrol_et()
        except Exception as e:
            print("Hata:", e)
        time.sleep(900) # 15 dakikada bir tarar

# Sistemi hem web sayfası hem de bot olarak aynı anda çalıştıran motor
if __name__ == "__main__":
    threading.Thread(target=bot_dongusu).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)