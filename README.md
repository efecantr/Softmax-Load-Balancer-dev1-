İstemci Taraflı Yük Dengeleyici (Softmax Load Balancer)
Bu proje, dağıtık sistemlerde performansları zamanla değişen (non-stationary) ve dalgalı (noisy) yanıt veren sunuculara gelen istekleri optimize etmek için yazılmış bir yük dengeleyici (load balancer) simülasyonudur. Temel amacımız toplam bekleme süresini (latency) en aza indirmektir.

Neden Softmax Algoritması Kullanıldı?
Klasik "Round-Robin" (sırayla) veya "Random" (rastgele) algoritmaları kör çalışır; sunucunun o an yavaşlayıp yavaşlamadığını umursamazlar.
Bu projede Softmax algoritmasını tercih ettik çünkü Softmax geçmiş yanıt sürelerine bakarak sistemi dinamik olarak günceller. Gecikmesi düşük (hızlı) sunuculara ağırlık verirken, yavaşlayan sunuculara giden istekleri azaltır. Ancak düşük bir ihtimalle de olsa diğer sunucuları yoklamaya (exploration) devam ederek zaman içindeki performans değişikliklerini kaçırmaz.

Nümerik Stabilite Çözümü
Softmax algoritmasının formülündeki üs alma (exponential) işlemi, değerler büyüdüğünde programlama dillerinde "Overflow" (Taşma) hatasına sebep olur ve programı çökertir.
Bu sorunu çözmek için Max-Shift yöntemini uyguladık. Hesaplamaya girmeden önce dizideki en yüksek ödül değerini bulup, formüldeki diğer tüm değerlerden çıkardık. Böylece math.exp() fonksiyonuna giren en büyük sayı sıfır oldu (e^0 = 1). Bu ufak matematiksel düzeltme sayesinde sistemin çökmesi (overflow) tamamen engellendi.

Agentic Kodlama Süreci
Bu proje tek bir prompt ile yapay zekaya yazdırılmamıştır. Gemini dil modeli, bir asistan ve kod inceleyici (mimar) rolünde kullanılarak "Agentic" bir yaklaşımla adım adım ilerlenmiştir:

Önce sadece sunucu sınıfı ve gecikme mantığı (Random Walk) tasarlandı.

Ardından Softmax algoritması entegre edildi.

Çıkan nümerik stabilite sorunları ve mantık hataları karşılıklı iterasyonlarla düzeltildi.

Çalışma Zamanı (Runtime) Analizi
Yazdığımız algoritmada asıl yük sunucu_sec metodundadır. Her istekte K adet (bizim kodumuzda 5) sunucu için döngü çalışır. Bu nedenle tek bir isteğin çalışma zamanı karmaşıklığı O(K)'dır.
Sisteme toplam N adet istek attığımızda (örneğin 10.000 istek) algoritmanın toplam zaman karmaşıklığı doğrusal olarak O(N * K) olur. Testlerimizde 10.000 istek ortalama 0.02 saniyede sorunsuz tamamlanmıştır.
