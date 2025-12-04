"""
Controller: Scraper Controller
Web scraping işlemlerini yöneten controller katmanı
"""
from flask import jsonify, session, Response
from app.models.scraper import ScraperModel
import pandas as pd
import io
import json


class ScraperController:
    """Scraping işlemlerini yöneten controller"""
    
    def __init__(self):
        self.model = ScraperModel()
    
    def scrape_data(self, base_url: str, start_id: int, count: int):
        """
        Veri kazıma işlemini gerçekleştir ve gerçek zamanlı progress döndür
        Generator fonksiyon - SSE (Server-Sent Events) için
        """
        def generate():
            def progress_callback(current, total, success_count, failed_count, current_id):
                progress_data = {
                    'status': 'progress',
                    'current': current,
                    'total': total,
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'current_id': current_id,
                    'percentage': round((current / total) * 100, 1)
                }
                yield f"data: {json.dumps(progress_data)}\n\n"
            
            # Scraping işlemini başlat
            results, success_count, failed_count = self.model.scrape_multiple(
                base_url, start_id, count, 
                progress_callback=lambda c, t, s, f, cid: list(progress_callback(c, t, s, f, cid))
            )
            
            # Sonuçları session'a kaydet
            session['scrape_results'] = results
            
            # Tamamlandı mesajı
            completion_data = {
                'status': 'complete',
                'total': count,
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    def scrape_data_sync(self, base_url: str, start_id: int, count: int):
        """
        Senkron veri kazıma - tüm işlem bitene kadar bekler
        """
        results_list = []
        success_count = 0
        failed_count = 0
        
        for i in range(count):
            current_id = start_id + i
            url = f"{base_url}{current_id}"
            
            try:
                data = self.model.scrape_single_fatura(url)
                data['ID'] = current_id
                results_list.append(data)
                success_count += 1
            except Exception as e:
                failed_count += 1
                print(f"ID {current_id} başarısız: {e}")
            
            # Rate limiting
            self.model.polite_sleep(i)
        
        # Sonuçları session'a kaydet
        session['scrape_results'] = results_list
        
        return {
            'status': 'success',
            'total': count,
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results_list
        }
    
    def export_to_excel(self, results: list) -> bytes:
        """
        Kazınan verileri Excel formatında döndür
        """
        if not results:
            raise ValueError("Dışa aktarılacak veri yok")
        
        # DataFrame oluştur
        df = pd.DataFrame(results)
        
        # Sütun sıralama - ID'yi başa al
        if 'ID' in df.columns:
            cols = ['ID'] + [col for col in df.columns if col != 'ID']
            df = df[cols]
        
        # Excel'e çevir (BytesIO kullanarak bellekte tut)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Fatura Verileri')
        
        output.seek(0)
        return output.getvalue()
