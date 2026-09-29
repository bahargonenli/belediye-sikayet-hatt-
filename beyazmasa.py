import sqlite3

def veritabani_olustur():
    conn = sqlite3.connect('beyaz_masa.db')
    cursor = conn.cursor()
    
    # Personel tablosu
    cursor.execute('''CREATE TABLE IF NOT EXISTS personeller 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       tc TEXT UNIQUE, 
                       sifre TEXT)''')
    
    # Şikayetler tablosu
    cursor.execute('''CREATE TABLE IF NOT EXISTS sikayetler 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       ad_soyad TEXT, 
                       tc TEXT, 
                       telefon TEXT, 
                       sikayet TEXT, 
                       durum TEXT DEFAULT 'Beklemede')''')
    
    conn.commit()
    conn.close()
    print("Veritabanı başarıyla oluşturuldu!")

veritabani_olustur()