import os
import requests
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def video_uret():
    print("Sistem başlatıldı. İçerik hazırlanıyor...")
    
    # 1. Buluttan rastgele bir İngilizce motivasyon sözü çekelim
    try:
        response = requests.get("https://quotable.io")
        if response.status_code == 200:
            veri = response.json()
            soz = f'"{veri["content"]}"\n\n- {veri["author"]}'
        else:
            soz = "Zorluklar, başarıya giden merdivenlerin basamaklarıdır."
    except:
        soz = "Vazgeçmediğin sürece asla kaybetmezsin."

    print(f"Seçilen Söz:\n{soz}")

    # 2. İnternetten dikey bir hazır video indirelim
    video_url = "https://mixkit.co"
    print("Arka plan videosu indiriliyor...")
    r = requests.get(video_url, stream=True)
    with open("arka_plan.mp4", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    # 3. MoviePy ile videoyu düzenleyelim (İlk 8 saniye)
    klip = VideoFileClip("arka_plan.mp4").subclip(0, 8)
    
    # Ekranın ortasına gelecek metni tasarlayalım
    yazi_klibi = TextClip(
        soz, 
        fontsize=28, 
        color='white', 
        font='Liberation-Sans',
        method='caption',
        size=(klip.w - 100, None)
    ).set_position('center').set_duration(8)

    # Video ve metni üst üste koyalım
    final_video = CompositeVideoClip([klip, yazi_klibi])

    # 4. Çıktıyı bulut sunucusuna kaydedelim
    print("Video render ediliyor (Bulut işlemcisi kullanılıyor)...")
    final_video.write_videofile(
        "output_shorts.mp4", 
        fps=24, 
        codec="libx264", 
        audio_codec="aac"
    )
    print("Video başarıyla üretildi: output_shorts.mp4")

if __name__ == "__main__":
    video_uret()
