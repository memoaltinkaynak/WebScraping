# Fatura Scraper - Azure Deployment

Flask MVC Web Application for Azure App Service

## Azure'a Deploy

### Gereksinimler
- Azure App Service (Python 3.11)
- Azure hesabı

### Deployment Steps

1. **Azure CLI ile deploy:**
```bash
az webapp up --name fatura-scraper --resource-group myResourceGroup --runtime "PYTHON:3.11"
```

2. **VS Code Azure Extension ile:**
- Azure extension'ı yükle
- Web App'e sağ tıklayıp "Deploy to Web App" seç

3. **GitHub Actions ile:**
- Repository'nizi GitHub'a push edin
- Azure Portal'dan Deployment Center > GitHub seçin

## Kullanıcı Bilgileri

Kullanıcı bilgilerini `run_app.py` dosyasından güncelleyin:

```python
USERS = {
    'Mustafa80': 'Mustafa80..123',
}
```

## Güvenlik

Production ortamı için `run_app.py` içinde:
- `app.secret_key` değiştirin
- `debug=False` yapın
- HTTPS kullanın

## Teknik Detaylar

- **Framework:** Flask 3.0
- **Python:** 3.11+
- **Mimari:** MVC
- **Port:** 8000 (Azure otomatik ayarlar)
