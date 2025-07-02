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
    soup = BeautifulSoup(response.content, "html.parser")
    videos = soup.select("div.item")
    novos_videos = []

    for video in videos:
        link_tag = video.select_one("a")
        title_tag = video.select_one("h3")
        img_tag = video.select_one("img")

        if link_tag and title_tag and img_tag:
            link = link_tag["href"]
            titulo = title_tag.text.strip()
            img = img_tag["src"]

            if titulo not in POSTAGENS:
                POSTAGENS[titulo] = True
                novos_videos.append((titulo, link, img))

    return novos_videos

def postar_nos_canais(videos):
    for titulo, link, img in videos:
        try:
            texto = f"{titulo}\n🔗 {link}"
            bot.send_photo(chat_id=CANAL_1, photo=img, caption=texto)
            time.sleep(2)
            bot.send_photo(chat_id=CANAL_2, photo=img, caption=texto)
        except Exception as e:
            print(f"Erro ao postar: {e}")

def main():
    while True:
        print("Verificando novos vídeos...")
        novos_videos = get_videos_site()
        if novos_videos:
            postar_nos_canais(novos_videos)
        time.sleep(1800)  # Espera 30 minutos

if __name__ == "__main__":
    main()
