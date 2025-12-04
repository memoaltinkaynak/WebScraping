# Fatura Scraper - Sunucu Kurulum Rehberi

Bu rehber, Fatura Scraper web uygulamasını Linux sunucusuna (Ubuntu/Debian) kurmak için adım adım talimatlar içerir.

## 🖥️ Sunucu Gereksinimleri

- **İşletim Sistemi:** Ubuntu 20.04+ / Debian 10+
- **RAM:** En az 1GB (2GB önerilir)
- **Python:** 3.8 veya üzeri
- **Port:** 80 (HTTP) veya 443 (HTTPS)

## 📦 Adım 1: Sistem Güncellemesi

```bash
sudo apt update
sudo apt upgrade -y
```

## 🐍 Adım 2: Python ve Gerekli Paketleri Kur

```bash
# Python 3 ve pip
sudo apt install python3 python3-pip python3-venv -y

# Nginx web server
sudo apt install nginx -y

# Supervisor (süreç yönetimi için)
sudo apt install supervisor -y
```

## 📂 Adım 3: Proje Dosyalarını Yükle

```bash
# Kullanıcı oluştur (opsiyonel)
sudo useradd -m -s /bin/bash fatura
sudo su - fatura

# Proje klasörü
cd /home/fatura
mkdir fatura-scraper
cd fatura-scraper

# Dosyaları yükle (FTP, Git veya SCP ile)
# Örnek: SCP ile
# scp -r /path/to/Web_Scraping/* fatura@sunucu-ip:/home/fatura/fatura-scraper/
```

## 🔧 Adım 4: Virtual Environment Oluştur

```bash
cd /home/fatura/fatura-scraper

# Virtual environment oluştur
python3 -m venv .venv

# Aktif et
source .venv/bin/activate

# Bağımlılıkları kur
pip install -r requirements.txt

# Gunicorn kur (production server)
pip install gunicorn
```

## ⚙️ Adım 5: Gunicorn Yapılandırması

`gunicorn_config.py` dosyası oluştur:

```python
# /home/fatura/fatura-scraper/gunicorn_config.py

bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/fatura/fatura-scraper/logs/access.log"
errorlog = "/home/fatura/fatura-scraper/logs/error.log"
loglevel = "info"
```

Log klasörü oluştur:
```bash
mkdir -p /home/fatura/fatura-scraper/logs
```

## 🔄 Adım 6: Systemd Servisi (Otomatik Başlatma)

Systemd servis dosyası oluştur:

```bash
sudo nano /etc/systemd/system/fatura-scraper.service
```

İçeriği:
```ini
[Unit]
Description=Fatura Scraper Web Application
After=network.target

[Service]
Type=notify
User=fatura
Group=fatura
WorkingDirectory=/home/fatura/fatura-scraper
Environment="PATH=/home/fatura/fatura-scraper/.venv/bin"
ExecStart=/home/fatura/fatura-scraper/.venv/bin/gunicorn -c gunicorn_config.py run_app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Servisi başlat:
```bash
sudo systemctl daemon-reload
sudo systemctl start fatura-scraper
sudo systemctl enable fatura-scraper
sudo systemctl status fatura-scraper
```

## 🌐 Adım 7: Nginx Reverse Proxy

Nginx yapılandırması:

```bash
sudo nano /etc/nginx/sites-available/fatura-scraper
```

İçeriği (HTTP):
```nginx
server {
    listen 80;
    server_name fatura.example.com;  # Kendi domain'inizi yazın

    # Static dosyalar
    location /static {
        alias /home/fatura/fatura-scraper/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Ana uygulama
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout ayarları
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Güvenlik başlıkları
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Log dosyaları
    access_log /var/log/nginx/fatura-scraper-access.log;
    error_log /var/log/nginx/fatura-scraper-error.log;
}
```

Aktif et:
```bash
sudo ln -s /etc/nginx/sites-available/fatura-scraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Adım 8: SSL Sertifikası (HTTPS)

Let's Encrypt ile ücretsiz SSL:

```bash
# Certbot kur
sudo apt install certbot python3-certbot-nginx -y

# SSL sertifikası al
sudo certbot --nginx -d fatura.example.com

# Otomatik yenileme testi
sudo certbot renew --dry-run
```

## 🔐 Adım 9: Güvenlik Ayarları

### Firewall (UFW)
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### Secret Key Değiştir
`run_app.py` dosyasında:
```python
app.secret_key = 'BURAYA_GUCLU_BIR_ANAHTAR_OLUSTURUN'
```

Güçlü anahtar oluştur:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Debug Modu Kapat
`run_app.py`:
```python
if __name__ == '__main__':
    app.run(debug=False)  # Production'da False!
```

### Kullanıcı Bilgilerini Değiştir
`run_app.py`:
```python
USERS = {
    'yeni_admin': 'guclu_sifre_123!@#',
}
```

## 📊 Adım 10: Log İzleme

### Uygulama Logları
```bash
# Gerçek zamanlı log izleme
tail -f /home/fatura/fatura-scraper/logs/access.log
tail -f /home/fatura/fatura-scraper/logs/error.log
```

### Systemd Logları
```bash
sudo journalctl -u fatura-scraper -f
```

### Nginx Logları
```bash
sudo tail -f /var/log/nginx/fatura-scraper-access.log
sudo tail -f /var/log/nginx/fatura-scraper-error.log
```

## 🔄 Güncelleme ve Yeniden Başlatma

### Uygulama Güncelleme
```bash
cd /home/fatura/fatura-scraper
git pull  # veya yeni dosyaları yükle

# Virtual environment aktif et
source .venv/bin/activate

# Yeni bağımlılıkları kur
pip install -r requirements.txt

# Servisi yeniden başlat
sudo systemctl restart fatura-scraper
```

### Hızlı Yeniden Başlatma
```bash
sudo systemctl restart fatura-scraper
sudo systemctl restart nginx
```

## 🩺 Sağlık Kontrolü

### Servis Durumu
```bash
sudo systemctl status fatura-scraper
sudo systemctl status nginx
```

### Port Kontrolü
```bash
sudo netstat -tlnp | grep :5000  # Gunicorn
sudo netstat -tlnp | grep :80     # Nginx
```

### Disk Kullanımı
```bash
df -h
du -sh /home/fatura/fatura-scraper/*
```

## 🔧 Sorun Giderme

### Uygulama Başlamıyor
```bash
# Log kontrol et
sudo journalctl -u fatura-scraper -n 50

# Manuel başlatma dene
cd /home/fatura/fatura-scraper
source .venv/bin/activate
gunicorn -c gunicorn_config.py run_app:app
```

### Nginx Hatası
```bash
# Konfigürasyon testi
sudo nginx -t

# Hata logları
sudo tail -50 /var/log/nginx/error.log
```

### 502 Bad Gateway
- Gunicorn çalışıyor mu kontrol et: `sudo systemctl status fatura-scraper`
- Port dinliyor mu: `sudo netstat -tlnp | grep :5000`
- Firewall kuralları: `sudo ufw status`

### Import Hataları
```bash
cd /home/fatura/fatura-scraper
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 📈 Performans Optimizasyonu

### Worker Sayısını Artır
`gunicorn_config.py`:
```python
workers = 8  # CPU sayısı * 2 + 1
```

### Nginx Cache
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;

location /static {
    proxy_cache my_cache;
    proxy_cache_valid 200 30d;
}
```

## 🔄 Yedekleme

### Veritabanı Yedeği (Kullanıcılar için)
```bash
# Kullanıcı bilgilerini yedekle
cp run_app.py run_app.py.backup
```

### Log Rotasyonu
`/etc/logrotate.d/fatura-scraper`:
```
/home/fatura/fatura-scraper/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0640 fatura fatura
}
```

## 🌍 Domain Ayarları

DNS kayıtları (domain sağlayıcınızdan):

```
A Record:
fatura.example.com -> SUNUCU_IP_ADRESI

CNAME (opsiyonel):
www.fatura.example.com -> fatura.example.com
```

## 📱 Mobil Erişim

Responsive tasarım sayesinde doğrudan mobil tarayıcıdan erişebilirsiniz:
- Chrome / Safari / Firefox
- Android / iOS / Windows

## ✅ Kontrol Listesi

- [ ] Sunucu güncellemesi yapıldı
- [ ] Python 3.8+ kurulu
- [ ] Nginx kurulu ve çalışıyor
- [ ] Uygulama dosyaları yüklendi
- [ ] Virtual environment oluşturuldu
- [ ] Bağımlılıklar kuruldu
- [ ] Gunicorn yapılandırıldı
- [ ] Systemd servisi oluşturuldu
- [ ] Nginx reverse proxy ayarlandı
- [ ] SSL sertifikası yüklendi
- [ ] Firewall kuralları ayarlandı
- [ ] Secret key değiştirildi
- [ ] Kullanıcı bilgileri güncellendi
- [ ] Debug modu kapatıldı
- [ ] Loglar kontrol edildi
- [ ] Tarayıcıdan erişim test edildi

## 🎉 Başarı!

Uygulamanız artık canlı:
- **URL:** https://fatura.example.com
- **Mobil:** Her yerden erişim
- **Güvenli:** HTTPS ile şifreli

---

**Destek:** [email protected]
**Tarih:** 2025-11-23
