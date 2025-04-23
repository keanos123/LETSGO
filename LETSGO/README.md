# Ekran + Kamera Canlı Yayın Sistemi

Bu depo, ekran ve webcam görüntünüzü Windows istemciden alıp VPS (78.135.85.65) üzerinde yayınlayabileceğiniz tam bir çözüm içerir.

## Bileşenler

```
.
├── client_app/          # Windows istemci
│   ├── streamer.py      # FFmpeg başlat / durdur + WebSocket dinleyicisi
│   └── requirements.txt
└── server/
    ├── nginx.conf       # nginx + nginx‑rtmp ayarları
    └── panel/           # Flask Socket.IO kontrol paneli
        ├── app.py
        ├── requirements.txt
        ├── templates/
        │   └── index.html
        └── static/
            └── app.js
```

## Sunucu Kurulumu (Ubuntu örneği)

```bash
sudo apt update && sudo apt install -y nginx libnginx-mod-rtmp python3-venv
# Nginx yapılandırmasını kopyla
sudo cp server/nginx.conf /etc/nginx/nginx.conf
sudo systemctl restart nginx

# Panel için
cd server/panel
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# arka planda çalıştır
FLASK_APP=app flask run --host 0.0.0.0 --port 5000
```

## İstemci Kurulumu (Windows)

1. FFmpeg indirin ve `ffmpeg.exe`'i PATH'e ekleyin.
2. Python 3 yüklü olmalı.
3. `client_app` klasöründe:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python streamer.py
```

## Kullanım

Tarayıcıdan `http://78.135.85.65:8181` adresine girin.

• "Yayını Başlat" ile ekran + kamera akışı başlar.
• "Kamera Aç/Kapa" kamerayı üst üste bindirmeyi açar/kapatır.
• "Durdur" ile yayın kesilir.

Video, HLS (m3u8) üzerinden `<video>` etiketi ile gösterilir.

## Notlar
- Tek yayıncı desteği vardır; ihtiyaç olursa `application live` altına farklı `stream` path'leri ekleyerek çoğaltılabilir.
- Windows ekran yakalama için FFmpeg `gdigrab` kullanır. OBS Screen‑Capture‑Recorder kurulu değilse FFmpeg `gdigrab` yerleşik olarak çalışır.
