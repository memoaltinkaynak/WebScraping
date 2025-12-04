// ==================== GLOBAL VARIABLES ====================
let scrapedData = [];
let isScrapingActive = false;

// ==================== DOM ELEMENTS ====================
const scrapeForm = document.getElementById('scrapeForm');
const startBtn = document.getElementById('startBtn');
const downloadBtn = document.getElementById('downloadBtn');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const progressPercent = document.getElementById('progressPercent');
const resultsCard = document.getElementById('resultsCard');
const alertBox = document.getElementById('alertBox');

// Stats elements
const statTotal = document.getElementById('statTotal');
const statProcessed = document.getElementById('statProcessed');
const statSuccess = document.getElementById('statSuccess');
const statFailed = document.getElementById('statFailed');

// ==================== EVENT LISTENERS ====================
if (scrapeForm) {
    scrapeForm.addEventListener('submit', handleScrapeSubmit);
}

if (downloadBtn) {
    downloadBtn.addEventListener('click', handleDownloadExcel);
}

// ==================== MAIN FUNCTIONS ====================

async function handleScrapeSubmit(e) {
    e.preventDefault();
    
    if (isScrapingActive) {
        showAlert('Kazıma işlemi zaten devam ediyor!', 'warning');
        return;
    }
    
    // Form değerlerini al
    const baseUrl = document.getElementById('base_url').value;
    const startId = parseInt(document.getElementById('start_id').value);
    const count = parseInt(document.getElementById('count').value);
    
    // Validasyon
    if (count < 1 || count > 10000) {
        showAlert('Kayıt sayısı 1 ile 10000 arasında olmalıdır!', 'error');
        return;
    }
    
    // UI Hazırla
    prepareUI(count);
    
    // Scraping başlat
    try {
        await startScraping(baseUrl, startId, count);
    } catch (error) {
        showAlert('Bir hata oluştu: ' + error.message, 'error');
        resetUI();
    }
}

async function startScraping(baseUrl, startId, count) {
    isScrapingActive = true;
    
    try {
        const response = await fetch('/api/scrape-sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                base_url: baseUrl,
                start_id: startId,
                count: count
            })
        });
        
        if (!response.ok) {
            throw new Error('Sunucu hatası: ' + response.status);
        }
        
        const data = await response.json();
        
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        
        // Sonuçları işle
        handleScrapingComplete(data);
        
    } catch (error) {
        console.error('Scraping error:', error);
        throw error;
    } finally {
        isScrapingActive = false;
    }
}

function prepareUI(totalCount) {
    // Butonları güncelle
    startBtn.disabled = true;
    startBtn.textContent = 'Kazıma Devam Ediyor...';
    downloadBtn.style.display = 'none';
    
    // Progress göster
    progressSection.style.display = 'block';
    resultsCard.style.display = 'none';
    alertBox.style.display = 'none';
    
    // Stats sıfırla
    statTotal.textContent = totalCount;
    statProcessed.textContent = '0';
    statSuccess.textContent = '0';
    statFailed.textContent = '0';
    
    // Progress bar sıfırla
    updateProgressBar(0);
}

function resetUI() {
    startBtn.disabled = false;
    startBtn.textContent = 'Kazımayı Başlat';
    isScrapingActive = false;
}

function handleScrapingComplete(data) {
    // Progress güncelle
    updateProgressBar(100);
    progressText.textContent = '✅ Tamamlandı!';
    
    // Stats güncelle
    statProcessed.textContent = data.total;
    statSuccess.textContent = data.success_count;
    statFailed.textContent = data.failed_count;
    
    // Verileri sakla
    scrapedData = data.results || [];
    
    // Sonuçları göster
    if (scrapedData.length > 0) {
        displayResults(scrapedData);
        downloadBtn.style.display = 'inline-block';
        showAlert(`✅ Kazıma tamamlandı! ${data.success_count} başarılı, ${data.failed_count} başarısız.`, 'success');
    } else {
        showAlert('⚠️ Hiç veri kazınamadı. Lütfen parametreleri kontrol edin.', 'warning');
    }
    
    // UI'ı sıfırla
    resetUI();
}

function updateProgressBar(percentage) {
    progressBar.style.width = percentage + '%';
    progressBar.querySelector('.progress-bar-text').textContent = Math.round(percentage) + '%';
    progressPercent.textContent = Math.round(percentage) + '%';
}

function displayResults(results) {
    if (!results || results.length === 0) {
        resultsCard.style.display = 'none';
        return;
    }
    
    // Kolonları al
    const columns = Object.keys(results[0]);
    
    // Başlık satırı oluştur
    const tableHeader = document.getElementById('tableHeader');
    tableHeader.innerHTML = columns.map(col => `<th>${escapeHtml(col)}</th>`).join('');
    
    // Veri satırları oluştur
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = results.map(row => {
        return '<tr>' + columns.map(col => {
            const value = row[col];
            return `<td>${escapeHtml(String(value || '-'))}</td>`;
        }).join('') + '</tr>';
    }).join('');
    
    // Tabloyu göster
    resultsCard.style.display = 'block';
    
    // Tabloya kaydır
    setTimeout(() => {
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

async function handleDownloadExcel() {
    if (scrapedData.length === 0) {
        showAlert('İndirilecek veri bulunamadı!', 'error');
        return;
    }
    
    try {
        downloadBtn.disabled = true;
        downloadBtn.textContent = 'İndiriliyor...';
        
        const response = await fetch('/api/download-excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ results: scrapedData })
        });
        
        if (!response.ok) {
            throw new Error('Excel indirme hatası');
        }
        
        // Blob'u indir
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fatura_data_${scrapedData.length}_kayit_${new Date().getTime()}.xlsx`;
        document.body.appendChild(a);
        a.click();
        
        // Temizlik
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showAlert('✅ Excel dosyası indirildi!', 'success');
        
    } catch (error) {
        showAlert('❌ Excel indirme hatası: ' + error.message, 'error');
    } finally {
        downloadBtn.disabled = false;
        downloadBtn.textContent = '📥 Excel İndir';
    }
}

// ==================== UTILITY FUNCTIONS ====================

function showAlert(message, type = 'info') {
    alertBox.textContent = message;
    alertBox.className = 'alert alert-' + type;
    alertBox.style.display = 'block';
    
    // Otomatik gizle
    setTimeout(() => {
        hideAlert();
    }, 5000);
    
    // Üste kaydır
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function hideAlert() {
    alertBox.style.display = 'none';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==================== LIVE PROGRESS (Alternative SSE Implementation) ====================
// Bu fonksiyon Server-Sent Events ile canlı progress göstermek için kullanılabilir

async function startScrapingWithSSE(baseUrl, startId, count) {
    isScrapingActive = true;
    
    const eventSource = new EventSource(
        `/api/scrape?base_url=${encodeURIComponent(baseUrl)}&start_id=${startId}&count=${count}`
    );
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.status === 'progress') {
            // Progress güncelle
            const percentage = (data.current / data.total) * 100;
            updateProgressBar(percentage);
            progressText.textContent = `ID ${data.current_id} işleniyor...`;
            
            // Stats güncelle
            statProcessed.textContent = data.current;
            statSuccess.textContent = data.success_count;
            statFailed.textContent = data.failed_count;
        } 
        else if (data.status === 'complete') {
            eventSource.close();
            handleScrapingComplete(data);
        }
    };
    
    eventSource.onerror = function(error) {
        console.error('SSE Error:', error);
        eventSource.close();
        showAlert('Bağlantı hatası oluştu!', 'error');
        resetUI();
        isScrapingActive = false;
    };
}

// ==================== INITIALIZATION ====================
console.log('✅ Fatura Scraper Script loaded');
