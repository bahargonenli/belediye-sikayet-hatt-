import os
import random
import string
import sqlite3
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont

try:
    import pyodbc
except ImportError:
    pyodbc = None

# Proje klasörünün içindeki templates klasörünü gösterir
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)

# Session yönetimi için gizli anahtar
app.secret_key = 'sultanbeyli_beyaz_masa_gizli_anahtar'

# Yüklenen dosyaların kaydedileceği klasör
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- VERİTABANI BAĞLANTI FONKSİYONU (MSSQL & Render/SQLite Otomatik Geçiş) ---
USE_SQLITE = False

def get_db_connection():
    global USE_SQLITE
    if not USE_SQLITE and pyodbc is not None:
        try:
            server = '.\\SQLEXPRESS'  
            database = 'BeyazMasaDB'  
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            conn = pyodbc.connect(conn_str, timeout=2)
            return conn
        except Exception as e:
            print(f"MS SQL Server bağlantısı kurulamadı ({e}). SQLite veritabanına geçiliyor...")
            USE_SQLITE = True

    # Render / Linux veya MS SQL Server olmayan durumlar için SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'beyaz_masa.db')
    conn = sqlite3.connect(db_path)
    return conn

# Veritabanını ve Eksik Sütunları Otomatik Kontrol Etme / Oluşturma
def veritabani_kontrol():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQLite için kontrol ve tablo oluşturma
        if isinstance(conn, sqlite3.Connection):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Tbl_Vatandaslar (
                    TcKimlik TEXT PRIMARY KEY,
                    Ad TEXT NOT NULL,
                    Soyad TEXT NOT NULL,
                    DogumTarihi TEXT NOT NULL,
                    Telefon TEXT NOT NULL,
                    Adres TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Tbl_Personel (
                    PersonelTc TEXT PRIMARY KEY,
                    Sifre TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Tbl_Talepler (
                    TalepID INTEGER PRIMARY KEY AUTOINCREMENT,
                    VatandasTc TEXT NOT NULL,
                    AdSoyad TEXT NOT NULL,
                    Telefon TEXT NOT NULL,
                    Adres TEXT NOT NULL,
                    Sikayet TEXT NOT NULL,
                    DosyaAdi TEXT,
                    Durum TEXT NOT NULL DEFAULT 'Bekliyor'
                )
            ''')
        else:
            # MS SQL Server için kontrol ve tablo oluşturma
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tbl_Vatandaslar' and xtype='U')
                CREATE TABLE Tbl_Vatandaslar (
                    TcKimlik VARCHAR(11) PRIMARY KEY,
                    Ad VARCHAR(50) NOT NULL,
                    Soyad VARCHAR(50) NOT NULL,
                    DogumTarihi VARCHAR(20) NOT NULL,
                    Telefon VARCHAR(15) NOT NULL,
                    Adres VARCHAR(255) NOT NULL
                )
            ''')

            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tbl_Personel' and xtype='U')
                CREATE TABLE Tbl_Personel (
                    PersonelTc VARCHAR(11) PRIMARY KEY,
                    Sifre VARCHAR(50) NOT NULL
                )
            ''')

            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tbl_Talepler' and xtype='U')
                CREATE TABLE Tbl_Talepler (
                    TalepID INT IDENTITY(1,1) PRIMARY KEY,
                    VatandasTc VARCHAR(11) NOT NULL,
                    AdSoyad VARCHAR(100) NOT NULL,
                    Telefon VARCHAR(15) NOT NULL,
                    Adres VARCHAR(255) NOT NULL,
                    Sikayet VARCHAR(MAX) NOT NULL,
                    DosyaAdi VARCHAR(255),
                    Durum VARCHAR(20) NOT NULL DEFAULT 'Bekliyor'
                )
            ''')
            
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Tbl_Talepler') AND name = 'Adres')
                ALTER TABLE Tbl_Talepler ADD Adres VARCHAR(255) NOT NULL DEFAULT 'Belirtilmedi'
            ''')
            
        conn.commit()
        conn.close()
        print("Veritabanı ve tablo yapıları başarıyla doğrulandı.")
    except Exception as e:
        print(f"Veritabanı otomatik kurulum hatası: {e}")

# Uygulama başladığında veritabanını doğrula (gunicorn için de hazır olur)
veritabani_kontrol()

# --- CAPTCHA (DOĞRULAMA KODU) FONKSİYONLARI ---
def generate_captcha_text(length=5):
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

@app.route('/captcha-image')
def captcha_image():
    text = generate_captcha_text(5)
    session['captcha'] = text  # Doğrulama kodunu session'a kaydediyoruz
    
    image = Image.new('RGB', (140, 45), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((15, 8), text, fill=(38, 95, 199), font=font)
    
    buf = BytesIO()
    image.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
# ---------------------------------------------

# Ana Sayfa
@app.route('/')
def anasayfa():
    return render_template('indexx.html')

# Başvuru Oluşturma Sayfası
@app.route('/sikayetolustur')
def sikayet_olustur():
    return render_template('sikayetolustur.html')

# Personel Giriş Sayfası
@app.route('/personelgrs')
def personel_giris():
    return render_template('personelgrs.html')

# Başvuru Sorgulama Sayfası
@app.route('/sorgula', methods=['GET', 'POST'])
def basvuru_sorgula():
    sonuclar = None
    aranan_tc = None
    
    if request.method == 'POST':
        aranan_tc = request.form.get('tc', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AdSoyad, VatandasTc, Telefon, Adres, Sikayet, DosyaAdi, Durum 
            FROM Tbl_Talepler 
            WHERE LTRIM(RTRIM(VatandasTc)) = ?
        ''', (aranan_tc,))
        
        sonuclar = cursor.fetchall()
        conn.close()
        
    return render_template('sorgula.html', sonuclar=sonuclar, aranan_tc=aranan_tc)
# Başvuru Ekleme ve Dosya Kaydetme İşlemi
@app.route('/ekle', methods=['POST'])
def basvuru_ekle():
    # Doğrulama Kodu Kontrolü
    kullanici_girdisi = request.form.get('captcha_input', '').strip().upper()
    gercek_captcha = session.get('captcha', '')
    
    if not kullanici_girdisi or kullanici_girdisi != gercek_captcha:
        return "Doğrulama kodu hatalı!", 400

    ad = request.form.get('ad')
    soyad = request.form.get('soyad')
    tc = request.form.get('tc')
    dogum_tarihi = request.form.get('dogum_tarihi')
    telefon = request.form.get('telefon')
    adres = request.form.get('adres')
    konu = request.form.get('konu')
    
    dosya = request.files.get('dosya')
    dosya_adi = None
    if dosya and dosya.filename != '':
        dosya_adi = secure_filename(dosya.filename)
        dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosya_adi))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vatandaş kaydı yoksa ekle (Hem MSSQL hem SQLite uyumlu)
    cursor.execute("SELECT 1 FROM Tbl_Vatandaslar WHERE TcKimlik = ?", (tc,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO Tbl_Vatandaslar (TcKimlik, Ad, Soyad, DogumTarihi, Telefon, Adres) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tc, ad, soyad, dogum_tarihi, telefon, adres))
    
    ad_soyad = f"{ad} {soyad}"
    cursor.execute('''
        INSERT INTO Tbl_Talepler (VatandasTc, AdSoyad, Telefon, Adres, Sikayet, DosyaAdi, Durum) 
        VALUES (?, ?, ?, ?, ?, ?, 'Bekliyor')
    ''', (tc, ad_soyad, telefon, adres, konu, dosya_adi))
    
    conn.commit()
    conn.close()
    
    return "Başarılı", 200

# Şikayetleri Listeleme ve Filtreleme
@app.route('/sikayetler')
def sikayetleri_listele():
    durum_filtresi = request.args.get('durum')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if durum_filtresi:
        cursor.execute('SELECT TalepID, VatandasTc, AdSoyad, Telefon, Adres, Sikayet, DosyaAdi, Durum FROM Tbl_Talepler WHERE Durum = ? ORDER BY TalepID DESC', (durum_filtresi,))
    else:
        cursor.execute('SELECT TalepID, VatandasTc, AdSoyad, Telefon, Adres, Sikayet, DosyaAdi, Durum FROM Tbl_Talepler ORDER BY TalepID DESC')
    
    sonuclar = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM Tbl_Talepler')
    toplam_sayi = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM Tbl_Talepler WHERE Durum = ?', ('Bekliyor',))
    bekliyor_sayisi = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM Tbl_Talepler WHERE Durum = ?', ('Dönüş Yapıldı',))
    donus_sayisi = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM Tbl_Talepler WHERE Durum = ?', ('Reddedildi',))
    red_sayisi = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template(
        'sikayetler.html', 
        sonuclar=sonuclar, 
        toplam_sayi=toplam_sayi,
        bekliyor_sayisi=bekliyor_sayisi,
        donus_sayisi=donus_sayisi,
        red_sayisi=red_sayisi
    )

# Durum Güncelleme İşlemi
@app.route('/durumguncelle/<int:id>', methods=['POST'])
def durum_guncelle(id):
    yeni_sonuc = request.form.get('sonuc')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Tbl_Talepler SET Durum = ? WHERE TalepID = ?', (yeni_sonuc, id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('sikayetleri_listele'))

# Başvuru Silme İşlemi
@app.route('/sil/<int:id>', methods=['POST'])
def basvuru_sil(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Tbl_Talepler WHERE TalepID = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('sikayetleri_listele'))

if __name__ == '__main__':
    veritabani_kontrol()
    app.run(debug=True)