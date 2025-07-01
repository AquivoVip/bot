
import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from datetime import datetime
import json

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
bot = Bot(token=TOKEN)

POSTED_LOG = "posted_log.json"

if not os.path.exists(POSTED_LOG):
    with open(POSTED_LOG, "w") as f:
        json.dump([], f)

def is_within_schedule():
    now = datetime.now()
    hour = now.hour + now.minute / 60
    return hour >= 13.5 or hour < 4.5  # Das 13h30 até 04h30

def load_posted_links():
    with open(POSTED_LOG, "r") as f:
        return json.load(f)

def save_posted_link(link):
    data = load_posted_links()
    data.append(link)
    with open(POSTED_LOG, "w") as f:
        json.dump(data, f)

def clean_title(raw_title):
    clean = raw_title.replace("fxggxt.com", "").replace("FXGGXT", "").strip()
    return clean

def fetch_latest_video():
    url = "https://fxggxt.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    videos = soup.find_all("div", class_="videoblock")
    for video in videos:
        link = video.find("a")["href"]
        full_link = "https://fxggxt.com" + link
        if full_link not in load_posted_links():
            title = video.find("img")["alt"]
            img_url = video.find("img")["src"]
            return clean_title(title), full_link, img_url
    return None, None, None

def download_file(url, filename):
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)

def post_to_channel(title, img_path, video_path):
    caption_img = f"{title}

–––––––––––––––––––––––––––
🦋 @ArquivoVIPcentral 🔞"
    bot.send_document(chat_id=CHANNEL_ID, document=open(img_path, "rb"), caption=caption_img, parse_mode=ParseMode.HTML)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧩 Arquivo VIP Central", url="https://t.me/ArquivoVIPcentral/"),
         InlineKeyboardButton("🔞 Acessar Studios B🔞YS", url="https://t.me/boystudios/")],
        [InlineKeyboardButton("🛒 Assinatura", url="https://t.me/ComboCompletoBot/")]
    ])
    bot.send_video(chat_id=CHANNEL_ID, video=open(video_path, "rb"), caption=" ", reply_markup=buttons)

def main():
    while True:
        if is_within_schedule():
            print("⏳ Verificando novos vídeos...")
            title, video_url, img_url = fetch_latest_video()
            if video_url:
                print(f"🔍 Novo vídeo detectado: {title}")
                img_file = "cover.jpg"
                vid_file = "video.mp4"
                download_file(img_url, img_file)

                # Aqui seria necessário implementar um downloader real de vídeo do link do vídeo
                # Este código é apenas estrutural. O download do vídeo depende da fonte.
                with open(vid_file, "wb") as f:
                    f.write(b"FAKE_VIDEO_DATA")

                post_to_channel(title, img_file, vid_file)
                save_posted_link(video_url)
        else:
            print("⏸️ Fora do horário de postagem. Dormindo...")
        time.sleep(60)

if __name__ == "__main__":
    main()
