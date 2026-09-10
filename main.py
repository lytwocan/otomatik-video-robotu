import os
import subprocess
import requests
from moviepy import VideoFileClip, CompositeVideoClip, ColorClip

KANAL_ADI = "rraenee"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEDEF_W, HEDEF_H = 1080, 1920
MAKS_SURE = 59  # YouTube Shorts limiti icin guvenli sinir
KLIP_SAYISI = 10
CIKTI_KLASORU = "shorts_ciktilari"


def klipleri_getir():
    """Kick API'sinden kanalin son kliplerini ceker, izlenmeye gore siralar."""
    url = f"https://kick.com/api/v2/channels/{KANAL_ADI}/clips"
    print(f"Kick API'sine istek atiliyor: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        clips = data.get("clips", [])
        if not clips:
            print("Klip listesi bos geldi.")
            return []

        clips_sirali = sorted(clips, key=lambda c: c.get("view_count", 0), reverse=True)
        secilenler = clips_sirali[:KLIP_SAYISI]
        print(f"{len(secilenler)} klip secildi (toplam {len(clips)} klip arasindan).")
        return secilenler
    except requests.exceptions.RequestException as e:
        print(f"Kick API istegi basarisiz oldu: {e}")
        return []
    except ValueError as e:
        print(f"Yanit JSON olarak parse edilemedi (Cloudflare engeli olabilir): {e}")
        return []


def m3u8_indir(m3u8_url, cikti_dosyasi):
    """ffmpeg kullanarak HLS (.m3u8) klibi duz bir mp4 dosyasina indirir."""
    print(f"ffmpeg ile klip indiriliyor: {m3u8_url}")
    komut = [
        "ffmpeg", "-y",
        "-user_agent", USER_AGENT,
        "-i", m3u8_url,
        "-c", "copy",
        cikti_dosyasi,
    ]
    sonuc = subprocess.run(komut, capture_output=True, text=True)
    if sonuc.returncode != 0:
        print(f"ffmpeg indirme hatasi:\n{sonuc.stderr[-1500:]}")
        return False
    if not os.path.exists(cikti_dosyasi) or os.path.getsize(cikti_dosyasi) == 0:
        print("Indirilen dosya bos veya olusmadi.")
        return False
    return True


def klibi_shorts_yap(klip, sira_no):
    """Tek bir klibi indirip dikey shorts formatina cevirir, dosya yolunu dondurur."""
    video_url = klip.get("video_url") or klip.get("clip_url")
    if not video_url:
        print(f"[{sira_no}] Klipte video_url yok, atlaniyor.")
        return None

    ham_dosya = f"kick_input_{sira_no}.mp4"
    if not m3u8_indir(video_url, ham_dosya):
        return None

    try:
        print(f"[{sira_no}] '{klip.get('title')}' dikey ekrana yerlestiriliyor...")
        orta_video = VideoFileClip(ham_dosya).resized(width=HEDEF_W)
        orta_video = orta_video.with_position("center")

        sure = min(MAKS_SURE, orta_video.duration)
        orta_video = orta_video.subclipped(0, sure)

        arka_plan = ColorClip(size=(HEDEF_W, HEDEF_H), color=(30, 30, 30)).with_duration(sure)
        final_shorts = CompositeVideoClip([arka_plan, orta_video], size=(HEDEF_W, HEDEF_H))

        cikti_yolu = os.path.join(CIKTI_KLASORU, f"rraenee_shorts_{sira_no:02d}.mp4")
        final_shorts.write_videofile(
            cikti_yolu,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=4,
        )
        return cikti_yolu
    except Exception as e:
        print(f"[{sira_no}] Video islenirken hata cikti, bu klip atlaniyor: {e}")
        return None
    finally:
        if os.path.exists(ham_dosya):
            os.remove(ham_dosya)


def shorts_uret():
    os.makedirs(CIKTI_KLASORU, exist_ok=True)
    klipler = klipleri_getir()

    basarili_sayisi = 0
    if klipler:
        for i, klip in enumerate(klipler, start=1):
            sonuc = klibi_shorts_yap(klip, i)
            if sonuc:
                basarili_sayisi += 1

    if basarili_sayisi == 0:
        print("Hicbir klip islenemedi. Yedek renkli ekran uretiliyor...")
        final_shorts = ColorClip(size=(HEDEF_W, HEDEF_H), color=(46, 204, 113)).with_duration(5)
        cikti_yolu = os.path.join(CIKTI_KLASORU, "rraenee_shorts_00.mp4")
        final_shorts.write_videofile(
            cikti_yolu,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=4,
        )

    print(f"Islem tamamlandi. Toplam {basarili_sayisi} shorts videosu uretildi.")


if __name__ == "__main__":
    shorts_uret()
