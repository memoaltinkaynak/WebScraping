"""
Fatura Scraper Web Application
MVC mimarisiyle Flask web uygulaması
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from functools import wraps
from app.controllers.scraper_controller import ScraperController
import io
from datetime import timedelta

# Flask app
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

import os

# Production secret key (Azure'da environment variable kullanın)
app.secret_key = os.environ.get('SECRET_KEY', 'fatura-scraper-2025-gizli-anahtar-degistir')
app.permanent_session_lifetime = timedelta(hours=24)

# Kullanıcı bilgileri (basit authentication için)
# Production'da database kullanılmalı!
USERS = {
    'Mustafa80': 'Mustafa80..123',
}

# Controller instance
scraper_controller = ScraperController()


# ==================== DECORATORS ====================

def login_required(f):
    """Login kontrolü için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Ana sayfa - login kontrolü yap"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login sayfası"""
    if request.method == 'POST':
        # JSON veya form data desteği
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '')
            password = data.get('password', '')
        else:
            username = request.form.get('username', '')
            password = request.form.get('password', '')
        
        # Kullanıcı doğrulama
        if username in USERS and USERS[username] == password:
            session.permanent = True
            session['username'] = username
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Giriş başarılı'})
            return redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Kullanıcı adı veya şifre hatalı!'})
            return render_template('login.html', error='Kullanıcı adı veya şifre hatalı!')
    
    # GET request
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Çıkış yap"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Ana dashboard - scraping işlemleri"""
    return render_template('dashboard.html', username=session['username'])


# ==================== API ENDPOINTS ====================

@app.route('/api/scrape', methods=['POST'])
@login_required
def api_scrape():
    """
    Scraping işlemini başlat (Server-Sent Events ile progress)
    """
    data = request.get_json()
    base_url = data.get('base_url', 'http://fatura.karansu.com/pay?=')
    start_id = int(data.get('start_id', 1))
    count = int(data.get('count', 100))
    
    # Controller'a ilet
    return scraper_controller.scrape_data(base_url, start_id, count)


@app.route('/api/scrape-sync', methods=['POST'])
@login_required
def api_scrape_sync():
    """
    Senkron scraping (tüm işlem bitene kadar bekler)
    """
    data = request.get_json()
    base_url = data.get('base_url', 'http://fatura.karansu.com/pay?=')
    start_id = int(data.get('start_id', 1))
    count = int(data.get('count', 100))
    
    try:
        result = scraper_controller.scrape_data_sync(base_url, start_id, count)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/download-excel', methods=['POST'])
@login_required
def api_download_excel():
    """
    Kazınan verileri Excel olarak indir
    """
    # Session'dan verileri al veya POST'tan
    if request.is_json:
        data = request.get_json()
        results = data.get('results', [])
    else:
        results = session.get('scrape_results', [])
    
    if not results:
        return jsonify({'error': 'İndirilecek veri bulunamadı'}), 404
    
    try:
        # Excel oluştur
        excel_data = scraper_controller.export_to_excel(results)
        
        # BytesIO'ya çevir
        output = io.BytesIO(excel_data)
        output.seek(0)
        
        # İndir
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'fatura_data_{len(results)}_kayit.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    # Azure App Service için port ayarı
    port = int(os.environ.get('PORT', 8000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
