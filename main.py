import os
import requests
import json
import time
from playwright.sync_api import sync_playwright
from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx

def rraenee_klip_indir_ve_duzenle():
    print("Tarayıcı tabanlı bot başlatılıyor...")
    
    # Playwright ile arka planda gizli bir Chrome tarayıcı açıyoruz
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Gerçek insan taklidi yapmak için tarayıcı kimliği (User-Agent) veriyoruz
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Kick API adresine tarayıcı ile giderek Cloudflare korumasını arkada aşmasını sağlıyoruz
        api_url = "https://kick.com"
        print("Kick verileri taranıyor...")
        
        try:
            page.goto(api_url, wait_until="networkidle")
            # Sayfadaki ham metni (JSON) çekiyoruz
            raw_content = page.locator("body").inner_text()
            data = json.loads(raw_content)
        except Exception as e:
            print(f"Tarayıcı ile veri çekilirken hata oluştu: {str(e)}")
            browser.close()
            return

        browser.close()

    clips = data.get("clips", [])
    if not clips:
        print("Son 7 güne ait popüler klip bulunamadı. Alternatif aranıyor...")
        return
        
    en_iyi_klip = clips[0]
    klip_linki = en_iyi_klip.get("video_url")
    klip_basligi = en_iyi_klip.get("title", "Komik RRaenee Ani")
    
    print(f"Başarıyla bulunan klip: {klip_basligi}")
    print("Klip bulut sunucusuna indiriliyor...")
    
    # Videoyu indir
    video_istek = requests.get(klip_linki, stream=True)
    with open("kick_input.mp4", "wb") as f:
        for chunk in video_istek.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                
    print("Düzenleme işlemi (Shorts formatı) başlatılıyor...")
    
    # MOVIEPY DÜZENLEME
    ana_video = VideoFileClip("kick_input.mp4")
    hedef_w, hedef_h = 1080, 1920
    
    # Karartılmış arka plan katmanı
    arka_plan = (ana_video
                 .resize(height=hedef_h)
                 .crop(x_center=ana_video.w*hedef_h/ana_video.h/2, y_center=hedef_h/2, width=hedef_w, height=hedef_h)
                 .colorx(0.3)) 

    # Ortadaki net video katmanı
    orta_video = ana_video.resize(width=hedef_w).set_position("center")
    
    final_shorts = CompositeVideoClip([arka_plan, orta_video], size=(hedef_w,深度=hedef_h))
    
    if final_shorts.duration > 30:
        final_shorts = final_shorts.subclip(0, 30)
        
    final_shorts.write_videofile(
        "rraenee_shorts.mp4",
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )
    print("Video başarıyla oluşturuldu: rraenee_shorts.mp4")

if __name__ == "__main__":
    rraenee_klip_indir_ve_duzenle()
