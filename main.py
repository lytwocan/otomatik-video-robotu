import os
import requests
import json
from playwright.sync_api import sync_playwright
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip

def rraenee_klip_indir_ve_duzenle():
    print("Tarayıcı tabanlı bot başlatılıyor...")
    klip_linki = None
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Engel riskini azaltmak için doğrudan klibin kendisine yönlendiriyoruz
            api_url = "https://kick.com"
            print("Kick verileri taranıyor...")
            
            page.goto(api_url, wait_until="networkidle", timeout=15000)
            raw_content = page.locator("body").inner_text()
            data = json.loads(raw_content)
            browser.close()
            
            clips = data.get("clips", [])
            if clips and len(clips) > 0:
                klip_linki = clips[0].get("video_url")
                print(f"Kick üzerinden popüler klip bulundu!")
        except Exception as e:
            print(f"Kick canlı verisi çekilirken zaman aşımı oluştu, yedek sistem başlatılıyor...")

    hedef_w, hedef_h = 1080, 1920

    # ARKA PLAN HAZIRLAMA (Garantili Yöntem)
    # İnternetten video indirmek yerine bulut sisteminde 10 saniyelik şık, koyu gri hazır bir arka plan oluşturuyoruz
    arka_plan = ColorClip(size=(hedef_w, hedef_h), color=(30, 30, 30)).set_duration(10)

    if klip_linki:
        try:
            print("Klip bulut sunucusuna indiriliyor...")
            video_istek = requests.get(klip_linki, stream=True, timeout=20)
            with open("kick_input.mp4", "wb") as f:
                for chunk in video_istek.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            
            print("Orijinal klip dikey ekrana yerleştiriliyor...")
            orta_video = VideoFileClip("kick_input.mp4").resize(width=hedef_w).set_position("center")
            
            # Video çok uzunsa sınırla
            sure = min(15, orta_video.duration)
            arka_plan = ColorClip(size=(hedef_w, hedef_h), color=(30, 30, 30)).set_duration(sure)
            orta_video = orta_video.subclip(0, sure)
            
            final_shorts = CompositeVideoClip([arka_plan, orta_video], size=(hedef_w, hedef_h))
        except Exception as e:
            print(f"Klip işlenirken hata çıktı, boş şablon üretiliyor: {str(e)}")
            klip_linki = None

    if not klip_linki:
        print("Sistem testi için logo/yazı şablonlu video üretiliyor...")
        # Kick engellediğinde hata vermemesi için kanal logolu/yazılı harika bir test şablonu basıyoruz
        from moviepy.editor import TextClip
        test_yazisi = TextClip(
            "RRaenee Komik Anlar\n\nÇok Yakında Burada!", 
            fontsize=50, 
            color='white', 
            font='Liberation-Sans',
            method='caption',
            size=(hedef_w - 200, None)
        ).set_position('center').set_duration(5)
        
        arka_plan = ColorClip(size=(hedef_w, hedef_h), color=(20, 20, 20)).set_duration(5)
        final_shorts = CompositeVideoClip([arka_plan, test_yazisi], size=(hedef_w, hedef_h))

    final_shorts.write_videofile(
        "rraenee_shorts.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )
    print("Video başarıyla diskte oluşturuldu!")

if __name__ == "__main__":
    rraenee_klip_indir_ve_duzenle()
