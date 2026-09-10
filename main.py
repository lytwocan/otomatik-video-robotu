import os
import requests
import json
import time
from playwright.sync_api import sync_playwright
from moviepy.editor import VideoFileClip, CompositeVideoClip

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
            
            api_url = "https://kick.com"
            print("Kick verileri taranıyor...")
            
            page.goto(api_url, wait_until="networkidle", timeout=30000)
            raw_content = page.locator("body").inner_text()
            data = json.loads(raw_content)
            browser.close()
            
            clips = data.get("clips", [])
            if clips:
                klip_linki = clips[0].get("video_url")
                print(f"Kick üzerinden popüler klip bulundu: {clips[0].get('title')}")
        except Exception as e:
            print(f"Kick canlı verisi çekilirken bir durum oluştu: {str(e)}")

    # YEDEK MEKANİZMA: Eğer Kick o an yanıt vermediyse boş dönmesin, test için açık bir klip kullansın
    if not klip_linki:
        print("Kick API o an yanıt vermedi veya boş döndü. Yedek klip devreye alınıyor...")
        klip_linki = "https://mixkit.co"

    print("Klip bulut sunucusuna indiriliyor...")
    video_istek = requests.get(klip_linki, stream=True)
    with open("kick_input.mp4", "wb") as f:
        for chunk in video_istek.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                
    print("Düzenleme işlemi (Shorts formatı) başlatılıyor...")
    
    # MOVIEPY DÜZENLEME
    ana_video = VideoFileClip("kick_input.mp4")
    hedef_w, hedef_h = 1080, 1920
    
    # Karartılmış arka plan
    arka_plan = (ana_video
                 .resize(height=hedef_h)
                 .crop(x_center=ana_video.w*hedef_h/ana_video.h/2, y_center=hedef_h/2, width=hedef_w, height=hedef_h)
                 .colorx(0.3)) 

    # Ortadaki net video
    orta_video = ana_video.resize(width=hedef_w).set_position("center")
    
    final_shorts = CompositeVideoClip([arka_plan, orta_video], size=(hedef_w, hedef_h))
    
    # Testlerin hızlı bitmesi için klibi ilk 10 saniye ile sınırlayalım
    final_shorts = final_shorts.subclip(0, min(10, final_shorts.duration))
        
    final_shorts.write_videofile(
        "rraenee_shorts.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )
    print("Video başarıyla oluşturuldu: rraenee_shorts.mp4")

if __name__ == "__main__":
    rraenee_klip_indir_ve_duzenle()
