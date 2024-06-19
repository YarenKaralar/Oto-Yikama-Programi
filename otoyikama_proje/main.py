#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 06:41:12 2024

@author: Yaren Karalar
"""

# -*- coding: utf-8 -*-

# main.py

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from Sifre import Ui_MainWindow_Sifre
from Hakkinda import Ui_Dialog
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog
from widgets import Ui_mwOtoYikama
import sqlite3


class Giris_ekrani(QtWidgets.QMainWindow):     #Sifreyi girmek için açılan ekran
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow_Sifre()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.sifre_kontrol)  #"ok" butonuna basınca sifre_kontrol fonksiyonunu çalıştırır
        self.ui.buttonBox.rejected.connect(self.close)     #"cancel" butonuna basınca programdan çıkar

    #Girilen sifre programın şifresi ile eşleşiyor mu?
    def sifre_kontrol(self):            
        sifre_ = self.ui.lneSifre.text()
        if sifre_ == "carwash123":      #Programa giriş yapabilmek için belirlenen şifre
            QMessageBox.information(self, "Başarılı", "ŞİFRE DOĞRU, programa giriş yapabilirsiniz!")
            self.open_main_app()
        else:
            QMessageBox.warning(self, "Hatalı Şifre", "ŞİFRE YANLIŞ, tekrar deneyiniz!")

    #Şifre ekranının kapanıp ana uygulama ekranının açılmasını sağlar
    def open_main_app(self):
        self.main_app = MainWindow()
        self.main_app.show()
        self.close()


class MainWindow(QtWidgets.QMainWindow, Ui_mwOtoYikama):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        
        self.cboxicdisyikama.stateChanged.connect(self.Hesapla)
        self.cboxkoltuktemizleme.stateChanged.connect(self.Hesapla)
        self.cboxboyakoruma.stateChanged.connect(self.Hesapla)
        self.cboxseramikkaplama.stateChanged.connect(self.Hesapla)
        self.cboxpastacila.stateChanged.connect(self.Hesapla)
        self.cboxmotoryikama.stateChanged.connect(self.Hesapla)
        
        self.baglanti_olustur()
        self.listele()
        self.Hesapla()
        self.applyStyles()
        
        # Telefon numarası için boşluklu yazma
        phone_regex = QtCore.QRegExp(r"\d{3} \d{3} \d{4}")
        phone_validator = QtGui.QRegExpValidator(phone_regex, self.lneTelefon)
        self.lneTelefon.setValidator(phone_validator)
        self.lneTelefon.setInputMask("000 000 0000")
        
        
        # Plaka için 9-10 karakter sınırlaması ve boşluklu yazma
        plate_regex = QtCore.QRegExp(r"[A-Za-z0-9 ]{9,10}")
        plate_validator = QtGui.QRegExpValidator(plate_regex, self.lnePlaka)
        self.lnePlaka.setValidator(plate_validator)
                   

        
    def applyStyles(self):
        # QSS stil tanımları
        style_sheet = """
        QPushButton {
            background-color: rgba(125, 3, 61, 0.5);  /* Butonun normal arka plan rengi */
            color: white;  /* Metin rengi */
            border: 1px solid #FFFFFF;  /* Kenarlık rengi ve genişliği */
            border-radius: 5px;  /* Köşe yuvarlaklığı */
            padding: 10px;  /* İç boşluk */
        }
        QPushButton:hover {
            background-color: rgb(231, 151, 204);  /* Butonun üzerine gelindiğinde arka plan rengi */
        }
        QPushButton:pressed {
            background-color: rgb(239, 204, 241);  /* Butona basıldığında arka plan rengi */
        }
        """
    
        # Butonlara stili uygulama
        self.btnIslemeAl.setStyleSheet(style_sheet)
        self.btnKayitSil.setStyleSheet(style_sheet)
        self.btnKayitAra.setStyleSheet(style_sheet)
        self.btnGuncelle.setStyleSheet(style_sheet)
        self.btnKayitListele.setStyleSheet(style_sheet)
        self.btnCikis.setStyleSheet(style_sheet)
       
        self.btnIslemeAl.clicked.connect(self.IslemeAl)
        self.btnIslemeAl.clicked.connect(self.listele)
        self.btnKayitSil.clicked.connect(self.KayitSil)
        self.btnKayitSil.clicked.connect(self.listele)
        self.btnKayitAra.clicked.connect(self.KayitAra)
        self.btnGuncelle.clicked.connect(self.Guncelle)
        self.btnGuncelle.clicked.connect(self.listele)
        self.btnKayitListele.clicked.connect(self.listele)
        self.btnCikis.clicked.connect(self.Cikis)
        self.btnHakkinda.clicked.connect(self.hakkindayi_ac)
        self.tableWidget.itemSelectionChanged.connect(self.doldur)
                        
        
    def veri_giris_kontrol(self, adsoyad, telefon):
        # Ad ve soyad sadece harften mi oluşuyor diye kontrol edilir.
        if not adsoyad.replace(" ", "").isalpha():
            QMessageBox.warning(self, "UYARI", "Ad yalnızca harf içermelidir.")
            return False
        # Telefon sadece rakamdan mı oluşuyor diye kontrol edilir.
        if not telefon.replace(" ", "").isdigit():
            QMessageBox.warning(self, "UYARI", "Telefon no yalnızca rakam içermelidir.")
            return False
        return True
    
    def IslemeAl(self):
        # Widget bilgilerinin formdan alınıp değişkene aktarılması
        _lnePlaka = self.lnePlaka.text()
        _lneAdSoyad = self.lneAdSoyad.text()
        _lneTelefon = self.lneTelefon.text()
        _timeEdit = self.timeEdit.time().toString("HH:mm")
        _lneTutar = self.lneTutar.text()
        _lneTeslimAlma = _timeEdit 
        
        if not self.veri_giris_kontrol(_lneAdSoyad, _lneTelefon):
            return
        
        #Checkbox seçenekleri işaretlendiyse adını yaz işaretlenmediyse "-" yaz.
        _cboxicdisyikama = "İç dış yıkama" if self.cboxicdisyikama.isChecked() else "-"
        _cboxkoltuktemizleme = "Koltuk temizleme" if self.cboxkoltuktemizleme.isChecked() else "-"
        _cboxboyakoruma = "Boya koruma" if self.cboxboyakoruma.isChecked() else "-"
        _cboxseramikkaplama = "Seramik kaplama" if self.cboxseramikkaplama.isChecked() else "-"
        _cboxpastacila = "Pasta, Cila" if self.cboxpastacila.isChecked() else "-"
        _cboxmotoryikama = "Motor yıkama" if self.cboxmotoryikama.isChecked() else "-"
        
        #Radio button seçeneklerinden hangisi işaretlendiyse onu değişkene aktar.
        if self.rbtnEft.isChecked():
            _rbtn = "Eft/Havale"
        elif self.rbtnKrediKart.isChecked():
            _rbtn = "Kredi Kart"
        elif self.rbtnNakit.isChecked():
            _rbtn = "Nakit"
        else:
            _rbtn = "-"
        
        # Veritabanı işlemleri
        try:
            self.curs.execute(
                "INSERT INTO otoyikama (Plaka, AdSoyad, Telefon, TeslimAlma, IcDisYikama, KoltukTemizleme, "
                "BoyaKoruma, SeramikKaplama, PastaCila, MotorYikama, Odeme, Tutar) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (_lnePlaka, _lneAdSoyad, _lneTelefon, _lneTeslimAlma, _cboxicdisyikama, 
                 _cboxkoltuktemizleme, _cboxboyakoruma, _cboxseramikkaplama, 
                 _cboxpastacila, _cboxmotoryikama, _rbtn, _lneTutar)
            )
            self.conn.commit()
            QMessageBox.information(self, "BİLGİ", "Kayıt Başarıyla Eklendi.")
            self.listele()          
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "HATA", "Kayıt Eklenirken Hata: " + str(e))    
    
    
    def baglanti_olustur(self):
        try:
            self.conn = sqlite3.connect("veritabani.db")
            self.curs = self.conn.cursor()
            self.sorguCreTblOtoYikama = (
                "CREATE TABLE IF NOT EXISTS otoyikama ("
                "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "
                "Plaka TEXT NOT NULL UNIQUE, "
                "AdSoyad TEXT NOT NULL, "
                "Telefon TEXT NOT NULL, "
                "TeslimAlma TEXT NOT NULL, "
                "IcDisYikama TEXT NOT NULL, "
                "KoltukTemizleme TEXT NOT NULL, "
                "BoyaKoruma TEXT NOT NULL, "
                "SeramikKaplama TEXT NOT NULL, "
                "PastaCila TEXT NOT NULL, "
                "MotorYikama TEXT NOT NULL, "
                "Odeme TEXT NOT NULL, "
                "Tutar TEXT NOT NULL)"
            )
        
            self.curs.execute(self.sorguCreTblOtoYikama)
            self.conn.commit()                     
        except sqlite3.Error as e:
            print("SQLite Veritabanı Hatası:", e)
    
    #Seçilen özelliklere göre ödenecek tutara fiyat eklenmesi
    def Hesapla(self):
        tutar=0
        if self.cboxicdisyikama.isChecked():
            tutar+=700
        if self.cboxkoltuktemizleme.isChecked():
            tutar+=350
        if self.cboxboyakoruma.isChecked():
            tutar+=2000
        if self.cboxseramikkaplama.isChecked():
            tutar+=3500
        if self.cboxpastacila.isChecked():
            tutar+=2800
        if self.cboxmotoryikama.isChecked():
            tutar+=1000
        self.lneTutar.setText(str(tutar))    
    
    
    #Eklenen kayıtın tabloya listelenmesi ve ekrandan bilgilerin silinmesi
    def listele(self):
        try:
            self.tableWidget.clear()
            self.tableWidget.setHorizontalHeaderLabels(('Arac No','Plaka', 'Ad Soyad', 'Telefon No', 
                                                        'Teslim Alma','İç Dış Yıkama', 'Koltuk Temizleme', 
                                                        'Boya Koruma', 'Seramik Kaplama', 
                                                        'Pasta, Cila', 'Motor Yıkama','Ödeme','Tutar'))
            self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            
            self.curs.execute("SELECT * FROM otoyikama")
            for satirIndeks, satirVeri in enumerate(self.curs):
                self.tableWidget.insertRow(satirIndeks)
                for sutunIndeks, sutunVeri in enumerate(satirVeri):
                    self.tableWidget.setItem(satirIndeks, sutunIndeks, QTableWidgetItem(str(sutunVeri)))
            
            self.lnePlaka.clear()
            self.lneAdSoyad.clear()
            self.lneTelefon.clear()
            self.lneTelefon.setText("")
            self.timeEdit.clear()
            self.lneTutar.clear()
            self.cboxicdisyikama.setChecked(False)
            self.cboxboyakoruma.setChecked(False)
            self.cboxkoltuktemizleme.setChecked(False)
            self.cboxmotoryikama.setChecked(False)
            self.cboxpastacila.setChecked(False)
            self.cboxseramikkaplama.setChecked(False)
            self.rbtnEft.setChecked(False)
            self.rbtnKrediKart.setChecked(False)
            self.rbtnNakit.setChecked(False)
            
            #Tabloya eklenen kayıt sayısını verir
            self.curs.execute("SELECT COUNT(*) FROM otoyikama")
            KayitSayisi = self.curs.fetchone()
            self.lneKayitSayisi.setText(str(KayitSayisi[0]))
            
            
        except sqlite3.Error as e:
            print("SQLite Hatası:", e)
    
    
    
    def KayitSil(self):
        cevap = QMessageBox.question(self, "KAYIT SİL", "Kaydı silmek istiyor musunuz?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            secili = self.tableWidget.selectedItems()
            if secili:
                silinecek = secili[1].text()  # Plaka sütunu
                try:
                    self.curs.execute("DELETE FROM otoyikama WHERE Plaka=?", (silinecek,))
                    self.conn.commit()
                    self.listele()
                    self.statusbar.showMessage("Kayıt Başarıyla Silindi...", 10000)
                except sqlite3.Error as hata:
                    self.statusbar.showMessage("Hata Oluştu: " + str(hata))
            else:
                self.statusbar.showMessage("Silinecek Kaydı Seçin.", 10000)
        else:
            self.statusbar.showMessage("Silme İşlemi İptal Edildi...", 10000)
    
    
    def KayitAra(self):
        #Kayıt aramak için 3 değişkene bakılıyor. Plaka, ad soyad ve telefon.
        aranan1 = self.lnePlaka.text()
        aranan2 = self.lneAdSoyad.text()
        aranan3 = self.lneTelefon.text()
        
        filtre = []
        if aranan1:
            filtre.append("Plaka = ?")
        if aranan2:
            filtre.append("AdSoyad = ?")
        if aranan3:
            filtre.append("Telefon = ?")
    
                   
        #Filtreleme kriterlerini birleştirme
        filtre_sorgusu = " OR ".join(filtre)
        
        if filtre_sorgusu:
            sorgu = " SELECT * FROM otoyikama WHERE " + filtre_sorgusu
            parametreler = tuple(filter(lambda x: x, [aranan1, aranan2, aranan3]))
            
            self.curs.execute(sorgu, parametreler)
            sonuclar = self.curs.fetchall()
            
            #Tabloyu temizle
            self.tableWidget.clearContents() #içerikleri temizle
            self.tableWidget.setRowCount(0)  #satır sayısını sıfırla
            
            for satirIndeks, satirVeri in enumerate(sonuclar):
                self.tableWidget.insertRow(satirIndeks)
                for sutunIndeks, sutunVeri in enumerate(satirVeri):
                    self.tableWidget.setItem(satirIndeks,sutunIndeks,
                                             QTableWidgetItem(str(sutunVeri)))
        else:
            QMessageBox.warning(None, "Uyarı", "Arama için en az bir kriter doldur.")
    
    
    def Guncelle(self):
        cevap = QtWidgets.QMessageBox.question(self,"GÜNCELLE","Güncellemek istiyor musunuz?",\
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if cevap == QtWidgets.QMessageBox.Yes:
            try:
                secili = self.tableWidget.selectedItems()
                if secili:
                    _Id = int(secili[0].text()) #Id sütunu için
                    _lnePlaka = self.lnePlaka.text()
                    _lneAdSoyad = self.lneAdSoyad.text()
                    _lneTelefon = self.lneTelefon.text()
                    _timeEdit = self.timeEdit.time().toString("HH:mm")
                    _lneTutar = self.lneTutar.text()
                    
                    _cboxicdisyikama = "İç Dış Yıkama" if self.cboxicdisyikama.isChecked() else "-"
                    _cboxkoltuktemizleme = "Koltuk Temizleme" if self.cboxkoltuktemizleme.isChecked() else "-"
                    _cboxboyakoruma = "Boya Koruma" if self.cboxboyakoruma.isChecked() else "-"
                    _cboxseramikkaplama = "Seramik Kaplama" if self.cboxseramikkaplama.isChecked() else "-"
                    _cboxpastacila = "Pasta, Cila" if self.cboxpastacila.isChecked() else "-"
                    _cboxmotoryikama = "Motor Yıkama" if self.cboxmotoryikama.isChecked() else "-"
                    
                    if self.rbtnEft.isChecked():
                        _rbtn = "Eft/Havale"
                    elif self.rbtnKrediKart.isChecked():
                        _rbtn = "Kredi Kart"
                    elif self.rbtnNakit.isChecked():
                        _rbtn = "Nakit"
                    else:
                        _rbtn = "-"
  
                                            
                    self.curs.execute("UPDATE otoyikama SET Plaka=?, AdSoyad=?, Telefon=?, TeslimAlma=?,\
                                      IcDisYikama=?, KoltukTemizleme=?, BoyaKoruma=?, SeramikKaplama=?,\
                                          PastaCila=?, MotorYikama=?, Odeme=?, Tutar=? WHERE id=?", \
                                        (_lnePlaka, _lneAdSoyad, _lneTelefon, _timeEdit, _cboxicdisyikama,\
                                         _cboxkoltuktemizleme, _cboxboyakoruma, _cboxseramikkaplama,\
                                             _cboxpastacila, _cboxmotoryikama, _rbtn, _lneTutar, _Id))                      
                          
                    self.conn.commit()
                    self.listele()   #Tabloyu güncelle
                    
                    self.statusbar.showMessage("Kayit Guncellendi...",10000)
                else:
                    self.statusbar.showMessage("Kaydi secin.",10000)
            except sqlite3.Error as hata:
                    self.statusbar.showMessage("Hata Olustu:" + str(hata))
        else:
            self.statusbar.showMessage("Guncelleme islemi iptal edildi",10000)
    
    #Tabloda satır numarasına basılan kaydın bilgilerini ekrana yazmak için
    def doldur(self):
            secili = self.tableWidget.selectedItems()
            if len(secili) > 0:
                self.lnePlaka.setText(secili[1].text())
                self.lneAdSoyad.setText(secili[2].text())
                self.lneTelefon.setText(secili[3].text())
                time = QtCore.QTime.fromString(secili[4].text(), "HH:mm")
                self.timeEdit.setTime(time)              
                icdisyikama = secili[5].text()
                self.cboxicdisyikama.setChecked(icdisyikama == "İç dış yıkama")
                koltuktemizleme = secili[6].text()
                self.cboxkoltuktemizleme.setChecked(koltuktemizleme == "Koltuk temizleme")
                boyakoruma = secili[7].text()
                self.cboxboyakoruma.setChecked(boyakoruma == "Boya koruma")
                seramikkaplama = secili[8].text()
                self.cboxseramikkaplama.setChecked(seramikkaplama == "Seramik kaplama")
                pastacila = secili[9].text()
                self.cboxpastacila.setChecked(pastacila == "Pasta, Cila")
                motoryikama = secili[10].text()
                self.cboxmotoryikama.setChecked(motoryikama == "Motor yıkama")
                odeme = secili[11].text()
                self.rbtnEft.setChecked(odeme == "Eft/Havale")
                self.rbtnKrediKart.setChecked(odeme == "Kredi Kart")
                self.rbtnNakit.setChecked(odeme == "Nakit")
                self.lneTutar.setText(secili[12].text())
                                                             
            else:
                # Secili bir öge yoksa, alanları temizle
                self.lnePlaka.clear()
                self.lneAdSoyad.clear()
                self.lneTelefon.clear()
                self.timeEdit.clear()
                self.lneTutar.clear()
                self.cboxicdisyikama.setChecked(False)
                self.cboxboyakoruma.setChecked(False)
                self.cboxkoltuktemizleme.setChecked(False)
                self.cboxmotoryikama.setChecked(False)
                self.cboxpastacila.setChecked(False)
                self.cboxseramikkaplama.setChecked(False)
                self.rbtnEft.setChecked(False)
                self.rbtnKrediKart.setChecked(False)
                self.rbtnNakit.setChecked(False)


    def hakkindayi_ac(self):
        self.hakkinda_dialog = QDialog()
        self.ui_hakkinda = Ui_Dialog()
        self.ui_hakkinda.setupUi(self.hakkinda_dialog)
        self.hakkinda_dialog.exec_()

    
    def Cikis(self):
            self.close()
        
    def closeEvent(self, event):
        cevap = QMessageBox.question(self,"ÇIKIŞ","Programdan çıkmak istiyor musunuz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.conn.close()  #Veritabanı bağlantısını kapatır
            event.accept()     #Uygulamayı kapatır
        else:
            event.ignore()     #Çıkış işlemini iptal eder     


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    giris_ekrani = Giris_ekrani()
    giris_ekrani.show()      #Program çalıştığında ilk olarak şifreli giriş ekranını açar.
    sys.exit(app.exec_())

