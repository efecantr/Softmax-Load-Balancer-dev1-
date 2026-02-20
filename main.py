import random
import math
import time

# --- 1. SUNUCU SINIFI ---
class Sunucu:
    def __init__(self, baslangic_gecikmesi):
        self.ortalama_gecikme = baslangic_gecikmesi

    def gecikme_getir(self):
        # Gürültü (Noisy) - Gauss dağılımı ile gerçekçi ağ dalgalanması
        gercek_gecikme = random.gauss(self.ortalama_gecikme, 5.0)
        
        # Zamanla değişim (Non-stationary) - Random Walk ile sunucu performans kayması
        self.ortalama_gecikme += random.gauss(0, 1.0) 
        
        # Gecikme süresi 0 veya negatif olamaz, en az 0.1 ms dönüyoruz
        return max(0.1, gercek_gecikme)

# --- 2. YÜK DENGELEYİCİ SINIFI (SOFTMAX) ---
class YukDengeleyici:
    def __init__(self, sunucu_sayisi, ogrenme_orani=0.1, sicaklik=1.0):
        self.sunucu_sayisi = sunucu_sayisi
        self.ogrenme_orani = ogrenme_orani  # Yeni verilere ne kadar güveneceğiz?
        self.sicaklik = sicaklik            # Keşif (Exploration) oranı
        
        # Başlangıçta tüm sunucuların tahmini ödülü (kalitesi) 0 olsun
        self.tahmini_oduller = [0.0] * sunucu_sayisi

    def sunucu_sec(self):
        # NÜMERİK STABİLİTE ÇÖZÜMÜ (Overflow Koruması)
        # En yüksek ödülü bulup hepsinden çıkarıyoruz ki math.exp() patlamasın.
        en_yuksek_odul = max(self.tahmini_oduller)
        
        usler = []
        for odul in self.tahmini_oduller:
            # (odul - en_yuksek_odul) işlemi ile en büyük değerin e^0 = 1 olmasını sağlıyoruz.
            hesaplanan_us = math.exp((odul - en_yuksek_odul) / self.sicaklik)
            usler.append(hesaplanan_us)
            
        toplam_us = sum(usler)
        
        # Olasılıkları hesapla
        olasiliklar = []
        for u in usler:
            olasiliklar.append(u / toplam_us)
            
        # Olasılıklara göre rastgele bir sunucu seç
        secilen_sunucu = random.choices(range(self.sunucu_sayisi), weights=olasiliklar, k=1)[0]
        
        return secilen_sunucu

    def sonucu_isle(self, secilen_sunucu, gecikme_suresi):
        # Gecikmeyi minimize etmek istediğimiz için ödülü negatif yapıyoruz
        odul = -gecikme_suresi
        
        # Q-Learning formülü ile tahmini ödülü güncelle
        eski_tahmin = self.tahmini_oduller[secilen_sunucu]
        yeni_tahmin = eski_tahmin + self.ogrenme_orani * (odul - eski_tahmin)
        
        self.tahmini_oduller[secilen_sunucu] = yeni_tahmin

# --- 3. SİMÜLASYONU BAŞLATAN ANA FONKSİYON ---
def simulasyonu_baslat():
    sunucu_sayisi = 5
    toplam_istek = 10000  # Stres testi için 10.000 istek yolluyoruz
    
    # Farklı başlangıç gecikmelerine sahip 5 sunucu
    baslangic_gecikmeleri = [10.0, 50.0, 20.0, 100.0, 200.0]
    sunucular = []
    
    for gecikme in baslangic_gecikmeleri:
        yeni_sunucu = Sunucu(baslangic_gecikmesi=gecikme)
        sunucular.append(yeni_sunucu)
        
    # Yük dengeleyiciyi başlatıyoruz (Sıcaklık 5.0 ile keşif oranını dengeliyoruz)
    dengeleyici = YukDengeleyici(sunucu_sayisi=sunucu_sayisi, ogrenme_orani=0.1, sicaklik=5.0)
    
    secim_sayilari = [0] * sunucu_sayisi
    toplam_gecikme = 0.0

    print(f"Simulasyon basliyor... Toplam {toplam_istek} istek gonderilecek.\n")
    
    # ÇALIŞMA ZAMANI ANALİZİ: Başlangıç
    baslangic_zamani = time.time()

    # İstekleri yolladığımız ana döngü
    for i in range(toplam_istek):
        secilen_index = dengeleyici.sunucu_sec()
        gecikme = sunucular[secilen_index].gecikme_getir()
        dengeleyici.sonucu_isle(secilen_index, gecikme)
        
        secim_sayilari[secilen_index] += 1
        toplam_gecikme += gecikme

    # ÇALIŞMA ZAMANI ANALİZİ: Bitiş
    bitis_zamani = time.time()
    calisma_suresi = bitis_zamani - baslangic_zamani

    # --- ÇIKTILAR ---
    print("--- SIMULASYON SONUCLARI ---")
    for index, sayi in enumerate(secim_sayilari):
        print(f"Sunucu {index} (Baslangic: {baslangic_gecikmeleri[index]}ms) -> {sayi} kez secildi.")
    
    print(f"\nToplam yasanan gecikme: {toplam_gecikme:.2f} ms")
    print(f"Ortalama gecikme (Latency): {(toplam_gecikme/toplam_istek):.2f} ms")
    print(f"Kodun toplam calisma suresi (Runtime): {calisma_suresi:.4f} saniye")

# Dosya doğrudan çalıştırıldığında simülasyonu başlat
if __name__ == "__main__":
    simulasyonu_baslat()