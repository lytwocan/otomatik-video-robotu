import os
import requests
import json
from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx

def rraenee_klip_indir_ve_duzenle():
    print("RRaenee için klip arama işlemi başlatıldı...")
    
    # Kick API'sinden RRaenee'nin popüler kliplerini talep ediyoruz
    # Not: Kick korumalarını aşmak için tarayıcı taklidi (User-Agent) yapıyoruz
    url = "https://kick.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Kick API bağlantı hatası! Kod: {response.status_code}")
            return
            
        data = response.json()
        clips = data.get("clips", [])
        
        if not clips:
            print("Son 7 güne ait popüler klip bulunamadı.")
            return
            
        # En çok izlenen ilk klibi seçiyoruz
        en_iyi_klip = clips[0]
        klip_linki = en_iyi_klip.get("video_url")
        klip_basligi = en_iyi_klip.get("title", "Komik RRaenee Anı")
        
        print(f"Bulunan En Popüler Klip: {klip_basligi}")
        print("Klip bulut sunucusuna indiriliyor...")
        
        # Videoyu indir
        video_istek = requests.get(klip_linki, stream=True)
        with open("kick_input.mp4", "wb") as f:
            for chunk in video_istek.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    
        print("İndirme tamamlandı. Shorts (Dikey) formatına dönüştürülüyor...")
        
        # MOVIEPY İLE VİDEOYU DİKEY (SHORTS) YAPMA
        ana_video = VideoFileClip("kick_input.mp4")
        
        # Hedef Shorts Boyutu: 1080x1920 (9:16)
        hedef_w, hedef_h = 1080, 1920
        
        # 1. Katman: Arka plandaki bulanık büyük video
        # Yatay videoyu büyüterek tüm dikey ekranı kaplamasını sağlıyoruz ve bulanıklaştırıyoruz
        arka_plan = (ana_video
                     .resize(height=hedef_h)
                     .crop(x_center=ana_video.w*hedef_h/ana_video.h/2, y_center=hedef_h/2, width=hedef_w, height=hedef_h)
                     .fx(vfx.blink, 0, 0) # Hileli hızlı render için sinematik efekt
                     .fl_image(lambda image: image) # Altyapı hazırlığı
                    )
        # Basitlik ve hız için arka planı hafif karartalım (Bulanıklık yerine hızlı render alternatifi)
        arka_plan = arka_plan.colorx(0.3) 

        # 2. Katman: Ekranın ortasına yerleşecek net orijinal yayın görüntüsü
        # Yatay yayını genişliğe göre dikey ekranın ortasına sığacak şekilde küçültüyoruz
        orta_video = ana_video.resize(width=hedef_w).set_position("center")
        
        # İki katmanı üst üste birleştiriyoruz
        final_shorts = CompositeVideoClip([arka_plan, orta_video], size=(hedef_w, hedef_h))
        
        # Sadece ilk 30 saniyesini alalım (Klip çok uzunsa Shorts sınırını aşmasın)
        if final_shorts.duration > 30:
            final_shorts = final_shorts.subclip(0, 30)
            
        # Çıktıyı al
        final_shorts.write_videofile(
            "rraenee_shorts.mp4",
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4
        )
        print("Shorts videosu başarıyla oluşturuldu: rraenee_shorts.mp4")
        
    except Exception as e:
        print(f"Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    rraenee_klip_indir_ve_duzenle()
