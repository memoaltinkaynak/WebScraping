@echo off
chcp 65001 > nul
title Fatura Scraper Web Uygulaması
color 0A

echo.
echo ═══════════════════════════════════════════════════════
echo     🚀 FATURA SCRAPER WEB UYGULAMASI 🚀
echo ═══════════════════════════════════════════════════════
echo.

REM Python virtual environment'ı aktif et
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment bulunamadı!
    echo    Önce: python -m venv .venv
    pause
    exit /b 1
)

REM Flask uygulamasını başlat
echo ✅ Uygulama başlatılıyor...
echo.
echo 📍 Yerel Erişim: http://127.0.0.1:5000
echo 📍 Ağ Erişimi:   http://[IP_ADRESINIZ]:5000
echo.
echo.
echo ⏹️  Durdurmak için Ctrl+C'ye basın
echo.
echo ═══════════════════════════════════════════════════════
echo.

python run_app.py

pause
