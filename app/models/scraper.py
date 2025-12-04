"""
Model: Scraper
Fatura kazıma işlemlerini gerçekleştiren model katmanı
"""
import requests
from bs4 import BeautifulSoup
import time
import random

# User-Agent rotasyonu
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36',
]

# Hız ayarları
MIN_DELAY = 0.01
MAX_DELAY = 0.03
LONG_PAUSE_EVERY = 1000
LONG_PAUSE_MIN = 0.5
LONG_PAUSE_MAX = 1


class ScraperModel:
    """Fatura scraping işlemlerini yöneten model sınıfı"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def polite_sleep(self, index: int) -> None:
        """Rate limiting için gecikme"""
        time.sleep(MIN_DELAY + random.random() * (MAX_DELAY - MIN_DELAY))
        if index > 0 and index % LONG_PAUSE_EVERY == 0:
            time.sleep(LONG_PAUSE_MIN + random.random() * (LONG_PAUSE_MAX - LONG_PAUSE_MIN))
    
    def fetch_with_retries(self, url: str, max_retries: int = 1) -> str:
        """HTTP isteği gönder, retry mantığıyla"""
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                resp = self.session.get(url, headers=headers, timeout=2)
                
                if resp.status_code == 429:
                    time.sleep(0.2)
                    continue
                if 500 <= resp.status_code < 600:
                    continue
                    
                resp.raise_for_status()
                return resp.text
            except Exception as e:
                last_err = e
        
        raise last_err if last_err else RuntimeError('Bilinmeyen istek hatası')
    
    def scrape_single_fatura(self, url: str) -> dict:
        """Tek bir fatura sayfasını kazı"""
        html = self.fetch_with_retries(url)
        soup = BeautifulSoup(html, 'html.parser')

        # Kullanıcı Bilgileri
        kullanici_bolum = soup.select_one('#cikti .d45')
        if not kullanici_bolum:
            raise ValueError("Kullanıcı bölümü bulunamadı")
        
        kullanici_adi = ""
        daire_no = ""
        fatura_donemi = ""
        abone_no = ""
        
        for div in kullanici_bolum.find_all('div'):
            strong = div.find('strong')
            span = div.find('span')
            if strong and span:
                text = strong.text.strip()
                if 'Kullanıcı Adı' in text:
                    kullanici_adi = span.text.strip()
                elif 'Daire No' in text:
                    daire_no = span.text.strip()
                elif 'Fatura Dönemi' in text:
                    fatura_donemi = span.text.strip()
                elif 'Abone Numarası' in text:
                    abone_no = span.text.strip()

        # Site Bilgileri
        site_bolum = soup.select_one('#cikti .d45r')
        site_adi = ""
        adres = ""
        ilce_il = ""
        
        if site_bolum:
            for div in site_bolum.find_all('div'):
                strong = div.find('strong')
                span = div.find('span')
                if strong and span:
                    text = strong.text.strip()
                    if 'Site Adı' in text:
                        site_adi = span.text.strip()
                    elif 'Adres' in text:
                        adres = span.text.strip()
                    elif 'İlçe / İl' in text:
                        ilce_il = span.text.strip()

        # Sayaç Okuma Bilgileri
        sayaç_tablo = soup.select_one('table.table2')
        sayaclar = {}
        
        if sayaç_tablo:
            rows = sayaç_tablo.find_all('tr')
            for tr in rows:
                tds = tr.find_all('td')
                if len(tds) >= 7:
                    cihaz = tds[0].text.strip()
                    oda = tds[1].text.strip()
                    oda_lower = oda.lower()
                    
                    # Sayaç türünü belirle
                    sayac_turu = None
                    if 'kalorimetre' in oda_lower:
                        sayac_turu = 'Kalorimetre'
                    elif 'sıcak su' in oda_lower or 'sicak su' in oda_lower:
                        sayac_turu = 'Sıcak Su'
                    elif 'pay ölçer' in oda_lower or 'payölçer' in oda_lower or 'pay olcer' in oda_lower:
                        sayac_turu = 'Pay Ölçer'
                    elif 'soğuk su' in oda_lower or 'soguk su' in oda_lower:
                        sayac_turu = 'Soğuk Su'
                    else:
                        if cihaz and cihaz != '-':
                            sayac_turu = oda.title()
                    
                    if sayac_turu:
                        original_tur = sayac_turu
                        counter = 1
                        while sayac_turu in sayaclar:
                            counter += 1
                            sayac_turu = f"{original_tur} {counter}"
                        
                        sayaclar[sayac_turu] = {
                            'Cihaz No': cihaz if cihaz != '-' else "",
                            'Tarih': tds[3].text.strip(),
                            'Önceki Değer': tds[4].text.strip(),
                            'Yeni Değer': tds[5].text.strip(),
                            'Tüketim': tds[6].text.strip()
                        }

        # Sonuç
        result = {
            'Kullanıcı Adı': kullanici_adi,
            'Daire No': daire_no,
            'Fatura Dönemi': fatura_donemi,
            'Abone Numarası': abone_no,
            'Site Adı': site_adi,
            'Adres': adres,
            'İlçe / İl': ilce_il,
        }
        
        # Dinamik sayaç bilgilerini ekle
        for sayac_turu, bilgiler in sayaclar.items():
            for key, value in bilgiler.items():
                result[f'{sayac_turu} {key}'] = value
        
        return result
    
    def scrape_multiple(self, base_url: str, start_id: int, count: int, progress_callback=None):
        """
        Birden fazla fatura kazı
        progress_callback: Her adımda çağrılacak fonksiyon (current, total, success_count, failed_count, current_id)
        """
        results = []
        success_count = 0
        failed_count = 0
        
        for i in range(count):
            current_id = start_id + i
            url = f"{base_url}{current_id}"
            
            try:
                data = self.scrape_single_fatura(url)
                data['ID'] = current_id
                results.append(data)
                success_count += 1
            except Exception as e:
                failed_count += 1
                print(f"ID {current_id} başarısız: {e}")
            
            # Progress callback
            if progress_callback:
                progress_callback(
                    current=i + 1,
                    total=count,
                    success_count=success_count,
                    failed_count=failed_count,
                    current_id=current_id
                )
            
            # Rate limiting
            self.polite_sleep(i)
        
        return results, success_count, failed_count
