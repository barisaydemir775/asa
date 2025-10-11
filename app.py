from flask import Flask, render_template, request, flash
from call_quality_analyzer import CallQualityAnalyzer
import os

app = Flask(__name__)
# Güvenlik için secret_key'i ortam değişkeninden al, yoksa geçici bir anahtar kullan.
# Üretim ortamında mutlaka bir ortam değişkeni olarak ayarlanmalıdır.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_for_testing_only')

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles both displaying the form and processing the submitted transcript.
    """
    results = None
    if request.method == 'POST':
        transcript = request.form.get('transcript', '').strip()

        if not transcript:
            # Kullanıcı boş bir form gönderirse hata mesajı göster.
            flash('Lütfen analiz için bir transkript metni girin.', 'danger')
        else:
            try:
                # Analiz modülünü kullanarak veriyi işle.
                analyzer = CallQualityAnalyzer(transcript)
                results = analyzer.analyze()
            except ValueError as e:
                # Analiz sırasında bir hata oluşursa (örn. geçersiz format)
                # kullanıcıyı bilgilendir.
                flash(f"Analiz hatası: {e}", 'danger')
            except Exception as e:
                # Beklenmedik diğer hatalar için genel bir mesaj göster.
                flash(f"Beklenmedik bir hata oluştu: {e}", 'danger')

    return render_template('index.html', results=results)

if __name__ == '__main__':
    # Geliştirme ortamında debug modunu aktif et.
    # Üretim ortamında bu False olmalıdır.
    app.run(debug=True, port=5001)