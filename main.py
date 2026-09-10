import os
import subprocess
import requests
from moviepy import VideoFileClip, CompositeVideoClip, ColorClip

KANAL_ADI = "rraenee"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEDEF_W, HEDEF_H = 1080, 1920
MAKS_SURE = 59  # YouTube Shorts limiti icin guvenli sinir


def en_iyi_klibi_bul():
    """Kick API'sinden kanalin son kliplerini ceker, en cok izlenen klibi secer."""
    url = f"https://kick.com/api/v2/channels/{KANAL_ADI}/clips"
    print(f"Kick API'sine istek atiliyor: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        clips = data.get("clips", [])
        if not clips:
            print("Klip listesi bos geldi.")
            return None

        en_iyi = max(clips, key=lambda c: c.get("view_count", 0))
        print(f"Secilen klip: '{en_iyi.get('title')}' - {en_iyi.get('view_count')} izlenme, {en_iyi.get('duration')} sn")
        return en_iyi
    except requests.exceptions.RequestException as e:
        print(f"Kick API istegi basarisiz oldu: {e}")
        return None
    except ValueError as e:
        print(f"Yanit JSON olarak parse edilemedi (Cloudflare engeli olabilir): {e}")
        return None


def m3u8_indir(m3u8_url, cikti_dosyasi="kick_input.mp4"):
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


def shorts_uret():
    klip = en_iyi_klibi_bul()
    final_shorts = None

    if klip:
        video_url = klip.get("video_url") or klip.get("clip_url")
        if video_url and m3u8_indir(video_url):
            try:
                print("Klip dikey ekrana yerlestiriliyor...")
                orta_video = VideoFileClip("kick_input.mp4").resize(width=HEDEF_W)
                orta_video = orta_video.set_position("center")

                sure = min(MAKS_SURE, orta_video.duration)
                orta_video = orta_video.subclip(0, sure)

                arka_plan = ColorClip(size=(HEDEF_W, HEDEF_H), color=(30, 30, 30)).set_duration(sure)
                final_shorts = CompositeVideoClip([arka_plan, orta_video], size=(HEDEF_W, HEDEF_H))
            except Exception as e:
                print(f"Video islenirken hata cikti, yedek sablona geciliyor: {e}")
                final_shorts = None

    if final_shorts is None:
        print("Gecerli klip bulunamadi. Yedek renkli ekran uretiliyor...")
        final_shorts = ColorClip(size=(HEDEF_W, HEDEF_H), color=(46, 204, 113)).set_duration(5)

    final_shorts.write_videofile(
        "rraenee_shorts.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
    )
    print("Video basariyla olusturuldu!")


if __name__ == "__main__":
    shorts_uret()
