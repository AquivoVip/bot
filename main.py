import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Configurações
TOKEN = os.getenv("TELEGRAM_TOKEN")
CANAL_1 = "-1002816936225"  # Arquivo vip🖤
CANAL_2 = "-1002840999372"  # World
POSTAGENS = {}

bot = Bot(token=TOKEN)

def get_videos_site():
    url = "https://fxggxt.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    videos = soup.select(".video-block a.video-image")
    return [("https://fxggxt.com" + v.get("href")) for v in videos if v.get("href")]

def get_video_details(link):
    res = requests.get(link)
    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.select_one("h1").text.strip()
    video_url = soup.select_one("video source").get("src")
    thumb = soup.select_one("video").get("poster")
    return title, video_url, thumb

def enviar_para_canal(chat_id, title, video_url, thumb, legenda_extra=""):
    caption = f"{title}\n▬▬▬▬▬▬▬▬▬▬▬▬▬\n{legenda_extra}".strip()
    bot.send_video(
        chat_id=chat_id,
        video=video_url,
        caption=caption,
        thumb=thumb,
        supports_streaming=True
    )

def main():
    while True:
        try:
            links = get_videos_site()
            for link in links:
                if link not in POSTAGENS:
                    title, video_url, thumb = get_video_details(link)

                    # Primeira postagem (imediata)
                    enviar_para_canal(CANAL_1, title, video_url, thumb)

                    # Segunda postagem (agendada 24h depois)
                    POSTAGENS[link] = {
                        "time": time.time(),
                        "title": title,
                        "video_url": video_url,
                        "thumb": thumb
                    }

            # Verifica vídeos agendados para postar no segundo canal
            agora = time.time()
            for link, info in list(POSTAGENS.items()):
                if agora - info["time"] >= 86400:
                    legenda = "🦋 @ArquivoVIPcentral 🔞"
                    enviar_para_canal(CANAL_2, info["title"], info["video_url"], info["thumb"], legenda)
                    del POSTAGENS[link]

        except Exception as e:
            print(f"[ERRO] {e}")
        
        time.sleep(300)  # Espera 5 minutos antes de repetir

if __name__ == "__main__":
    main()
