# Fatura Scraper - MVC Web Uygulaması

Modern, responsive ve güvenli web tabanlı fatura kazıma sistemi. Flask MVC mimarisi ile geliştirilmiştir.

## 🎯 Özellikler

### Web Arayüzü
- ✅ **Güvenli Giriş Sistemi** - Kullanıcı adı ve şifre ile giriş
- ✅ **Responsive Tasarım** - Mobil, tablet ve masaüstü uyumlu
- ✅ **Gerçek Zamanlı İlerleme** - Kazıma işleminin canlı takibi
- ✅ **İstatistikler** - Başarılı/başarısız kayıt sayıları
- ✅ **Sonuç Tablosu** - Kazınan verilerin görüntülenmesi
- ✅ **Excel Export** - Verileri Excel olarak indirme

### Teknik Özellikler
- 🏗️ **MVC Mimarisi** - Model, View, Controller ayrımı
- 🔒 **Session Yönetimi** - Güvenli oturum kontrolü
- 🚀 **Hızlı Kazıma** - 15-25 istek/saniye
- 📊 **Dinamik Sayaç Desteği** - Sınırsız sayaç türü
- 💾 **Excel Export** - Pandas ve openpyxl ile
- 🌐 **AJAX İstekleri** - Sayfa yenilemeden işlem

## 📁 Proje Yapısı

```
Web_Scraping/
│
├── app/                          # Ana uygulama klasörü
│   ├── models/                   # Model katmanı (veri işleme)
│   │   ├── __init__.py
│   │   └── scraper.py           # Kazıma mantığı
│   │
│   ├── controllers/              # Controller katmanı (iş mantığı)
│   │   ├── __init__.py
│   │   └── scraper_controller.py
│   │
│   ├── templates/                # HTML şablonları
│   │   ├── login.html           # Giriş sayfası
│   │   └── dashboard.html       # Ana panel
│   │
│   ├── static/                   # Statik dosyalar
│   │   ├── css/
│   │   │   └── style.css        # Tüm CSS stilleri
│   │   └── js/
│   │       └── script.js        # Frontend JavaScript
│   │
│   └── __init__.py
│
├── run_app.py                    # Flask uygulaması (ana dosya)
├── requirements.txt              # Python bağımlılıkları
├── scraping.py                   # Eski CLI versiyonu
├── run_scraper.bat              # Windows batch dosyası
└── README.md                     # Bu dosya
```

## 🚀 Kurulum

### 1. Python Sanal Ortamı (varsa aktif et)

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Gerekli Kütüphaneleri Yükle

```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Başlat

```bash
python run_app.py
```

Uygulama şu adreslerde çalışacaktır:
- **Yerel:** http://127.0.0.1:5000
- **Ağ:** http://[IP_ADRESINIZ]:5000

## 🔐 Kullanıcı Girişi

Varsayılan hesaplar:

| Kullanıcı Adı | Şifre       |
|---------------|-------------|
| admin         | admin123    |
| user1         | password123 |
| demo          | demo123     |

> **⚠️ ÖNEMLİ:** Production ortamında bu kullanıcı bilgilerini değiştirin!

## 📖 Kullanım

### 1. Giriş Yapma
- Tarayıcıda uygulamayı açın
- Kullanıcı adı ve şifre ile giriş yapın

### 2. Veri Kazıma
- **Base URL:** Hedef site adresi (varsayılan: `http://fatura.karansu.com/pay?=`)
- **Başlangıç ID:** İlk kayıt numarası
- **Kayıt Sayısı:** Kazınacak toplam kayıt (max 10000)

### 3. Sonuçları İndirme
- Kazıma tamamlandığında "Excel İndir" butonu görünür
- Tıklayarak tüm verileri Excel formatında indirin

## 🏗️ MVC Mimarisi

### Model Katmanı (`app/models/scraper.py`)
```python
class ScraperModel:
    - scrape_single_fatura()  # Tek fatura kazı
    - scrape_multiple()       # Toplu kazıma
    - fetch_with_retries()    # HTTP istekleri
    - polite_sleep()          # Rate limiting
```

### Controller Katmanı (`app/controllers/scraper_controller.py`)
```python
class ScraperController:
    - scrape_data_sync()      # Senkron kazıma
    - export_to_excel()       # Excel export
```

### View Katmanı (`app/templates/`)
- **login.html** - Giriş formu
- **dashboard.html** - Ana panel, form, tablo

## 🌐 Sunucuya Deploy

### Gunicorn ile Production Modu

```bash
# Gunicorn kur
pip install gunicorn

# Uygulamayı çalıştır (4 worker)
gunicorn -w 4 -b 0.0.0.0:5000 run_app:app
```

### Systemd Servisi (Linux)

`/etc/systemd/system/fatura-scraper.service`:

```ini
[Unit]
Description=Fatura Scraper Web Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/Web_Scraping
Environment="PATH=/path/to/Web_Scraping/.venv/bin"
ExecStart=/path/to/Web_Scraping/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 run_app:app

[Install]
WantedBy=multi-user.target
```

Başlat:
```bash
sudo systemctl daemon-reload
sudo systemctl start fatura-scraper
sudo systemctl enable fatura-scraper
```

### Nginx Reverse Proxy

`/etc/nginx/sites-available/fatura-scraper`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/Web_Scraping/app/static;
    }
}
```

## 🔒 Güvenlik Önerileri

### 1. Secret Key Değiştir
`run_app.py` dosyasında:
```python
app.secret_key = 'rastgele-gizli-anahtar-buraya'
```

### 2. Debug Modunu Kapat
```python
app.run(debug=False)  # Production'da
```

### 3. Kullanıcı Bilgilerini Değiştir
```python
USERS = {
    'yeni_admin': 'guclu_sifre_123',
}
```

### 4. HTTPS Kullan
- Let's Encrypt ile ücretsiz SSL sertifikası
- Certbot kurulumu önerilir

### 5. Firewall Kuralları
```bash
# Sadece 80 ve 443 portlarını aç
ufw allow 80/tcp
ufw allow 443/tcp
```

## 📊 API Endpoints

### Authentication
- `GET /` - Ana sayfa (yönlendirme)
- `GET /login` - Login formu
- `POST /login` - Giriş işlemi
- `GET /logout` - Çıkış
- `GET /dashboard` - Ana panel (login required)

### Scraping API
- `POST /api/scrape-sync` - Senkron kazıma
  ```json
  {
    "base_url": "http://fatura.karansu.com/pay?=",
    "start_id": 1,
    "count": 100
  }
  ```

- `POST /api/download-excel` - Excel export
  ```json
  {
    "results": [...]
  }
  ```

## 🛠️ Geliştirme

### Yeni Kullanıcı Ekleme
`run_app.py`:
```python
USERS = {
    'yeni_user': 'yeni_sifre',
}
```

### CSS Stilleri Değiştirme
`app/static/css/style.css` - CSS değişkenleri:
```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
}
```

### Yeni Route Ekleme
`run_app.py`:
```python
@app.route('/yeni-sayfa')
@login_required
def yeni_sayfa():
    return render_template('yeni.html')
```

## 🐛 Hata Giderme

### Port Zaten Kullanılıyor
```bash
# Port 5000'i kullanan işlemi bul
netstat -ano | findstr :5000

# İşlemi sonlandır
taskkill /PID <PID> /F
```

### Import Hataları
```bash
# Tüm bağımlılıkları tekrar yükle
pip install -r requirements.txt --force-reinstall
```

### Template Bulunamadı
- Template yolunu kontrol et: `app/templates/`
- `run_app.py` içinde template_folder doğru mu?

### Static Dosyalar Yüklenmiyor
- Static yolu kontrol et: `app/static/`
- Tarayıcı cache'ini temizle (Ctrl+Shift+Delete)

## 📈 Performans

### Hız Ayarları
`app/models/scraper.py`:
```python
MIN_DELAY = 0.01  # İstekler arası minimum gecikme
MAX_DELAY = 0.03  # İstekler arası maksimum gecikme
```

### Worker Sayısı
```bash
# Daha fazla paralel işlem için
gunicorn -w 8 -b 0.0.0.0:5000 run_app:app
```

## 📝 Değişiklik Geçmişi

### v2.0.0 (2025-11-23)
- ✨ MVC mimarisi ile yeniden yazıldı
- ✨ Web arayüzü eklendi
- ✨ Kullanıcı girişi sistemi
- ✨ Responsive tasarım
- ✨ Excel export özelliği
- ✨ Gerçek zamanlı ilerleme takibi

### v1.0.0
- 🚀 İlk CLI versiyonu
- 📊 Dinamik sayaç desteği
- ⚡ Hız optimizasyonları

## 📞 Destek

Sorularınız için:
- 📧 Email: [email protected]
- 🐛 Issues: GitHub repository

## 📄 Lisans

Bu proje özel kullanım içindir. Ticari kullanım için izin gereklidir.

---

**© 2025 Fatura Scraper - Tüm hakları saklıdır**
