# Sultanbeyli Belediyesi - Beyaz Masa Destek ve Şikayet Hattı

Vatandaşların belediyeye online olarak şikayet, talep ve başvurularını iletebildiği, başvurularının güncel durumunu TC kimlik numaralarıyla sorgulayabildiği ve belediye personelinin gelen başvuruları inceleyip yönetebildiği Flask tabanlı web uygulaması.

---

## 🚀 Özellikler

- **Vatandaş İşlemleri:**
  - **Başvuru Oluşturma:** Ad, soyad, TC kimlik no, doğum tarihi, telefon, adres, başvuru metni ve ek dosya/görsel yükleme.
  - **CAPTCHA Güvenliği:** Otomatik üretilen görsel doğrulama kodu (CAPTCHA) ile güvenli form gönderimi.
  - **Başvuru Sorgulama:** Vatandaşların TC kimlik numaralarını girerek başvurularının sonucunu ve durumunu görüntüleyebilmesi.

- **Personel / Yönetim Paneli:**
  - Personel girişi ve yetkilendirme.
  - Tüm talepleri listeleme ve durumlarına göre filtreleme (*Bekliyor*, *Dönüş Yapıldı*, *Reddedildi*).
  - Talep durumu güncelleme (Sonuçlandırma/Cevaplama).
  - Talep silme işlemi.

---

## 🛠️ Kullanılan Teknolojiler

- **Backend:** Python, Flask, Werkzeug
- **Veritabanı:** Microsoft SQL Server (pyodbc), SQLite alternatifi
- **Güvenlik & Yardımcı Kütüphaneler:** Pillow (PIL) - Dinamik CAPTCHA üretimi
- **Frontend:** HTML5, CSS3, Jinja2 Template Engine

---

## 📂 Proje Yapısı

```plaintext
├── app.py                  # Ana Flask uygulama dosyası ve yönlendirmeler
├── beyazmasa.py            # SQLite test ve yedek veritabanı oluşturma betiği
├── BeyazMasaDB.sql         # MS SQL Server veritabanı ve tablo şeması
├── SQLQuery1.sql           # Tablo oluşturma sorguları
├── requirements.txt        # Gerekli Python kütüphaneleri
├── .gitignore              # Git takip dışı bırakma kuralları
├── templates/              # HTML şablonları
│   ├── indexx.html         # Ana sayfa
│   ├── sikayetolustur.html # Başvuru oluşturma sayfası
│   ├── sorgula.html        # Başvuru sorgulama sayfası
│   ├── personelgrs.html    # Personel giriş sayfası
│   └── sikayetler.html     # Personel talep yönetim paneli
└── static/                 # CSS ve görsel dosyaları
    ├── css/                # Sayfa stilleri
    └── uploads/            # Vatandaşların yüklediği ek dosyalar
```

---

## ⚙️ Kurulum ve Çalıştırma

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/bahargonenli/belediye-sikayet-hatt-.git
cd belediye-sikayet-hatt-
```

### 2. Sanal Ortam Oluşturun ve Aktif Edin
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Veritabanını Hazırlayın
- **MS SQL Server** kullanıyorsanız:
  - SQL Server Management Studio (SSMS) üzerinde `BeyazMasaDB.sql` dosyasını çalıştırın veya `app.py` otomatik olarak bağlantı sağlandığında eksik tabloları oluşturacaktır.
  - `app.py` içindeki `get_db_connection()` fonksiyonundaki sunucu adını (`.\\SQLEXPRESS`) kendi yerel SQL Server örneğinize göre düzenleyin.

### 5. Uygulamayı Başlatın
```bash
python app.py
```
Tarayıcınızdan `http://127.0.0.1:5000/` adresine giderek uygulamayı kullanabilirsiniz.
