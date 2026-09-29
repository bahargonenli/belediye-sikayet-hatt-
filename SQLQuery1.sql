DROP TABLE IF EXISTS Tbl_Talepler;
DROP TABLE IF EXISTS Tbl_Personel;
DROP TABLE IF EXISTS Tbl_Vatandaslar;
GO

CREATE TABLE Tbl_Vatandaslar (
    TcKimlik VARCHAR(11) PRIMARY KEY,
    Ad VARCHAR(50) NOT NULL,
    Soyad VARCHAR(50) NOT NULL,
    DogumTarihi VARCHAR(20) NOT NULL,
    Telefon VARCHAR(15) NOT NULL,
    Adres VARCHAR(255) NOT NULL
);
GO

CREATE TABLE Tbl_Personel (
    PersonelTc VARCHAR(11) PRIMARY KEY,
    Sifre VARCHAR(50) NOT NULL
);
GO

CREATE TABLE Tbl_Talepler (
    TalepID INT IDENTITY(1,1) PRIMARY KEY,
    VatandasTc VARCHAR(11) NOT NULL,
    AdSoyad VARCHAR(100) NOT NULL,
    Telefon VARCHAR(15) NOT NULL,
    Adres VARCHAR(255) NOT NULL,
    Sikayet VARCHAR(MAX) NOT NULL,
    DosyaAdi VARCHAR(255),
    Durum VARCHAR(20) NOT NULL DEFAULT 'Bekliyor',
    CONSTRAINT FK_Talepler_Vatandas FOREIGN KEY (VatandasTc) 
        REFERENCES Tbl_Vatandaslar(TcKimlik) ON DELETE CASCADE
);
GO

INSERT INTO Tbl_Personel (PersonelTc, Sifre) VALUES ('12345678900', 'bahar123');
INSERT INTO Tbl_Personel (PersonelTc, Sifre) VALUES ('24681012141', 'ahmetbelediye');
GO