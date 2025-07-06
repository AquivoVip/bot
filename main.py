import os
import time
import requests
from dotenv import load_dotenv
from telegram import Bot, InputMediaVideo
from telegram.error import TelegramError

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_1_ID = os.getenv("CANAL_1_ID")
CANAL_2_ID = os.getenv("CANAL_2_ID")

bot = Bot(token=BOT_TOKEN)
SITE_URL = "https://fxggxt.com/wp-json/wp/v2/posts"

def baixar_video(link, nome_arquivo):
    try:
        resposta = requests.get(link, timeout=15)
        with open(nome_arquivo, "wb") as f:
            f.write(resposta.content)
        return True
    except Exception as e:
        print(f"Erro ao baixar vídeo: {e}")
        return False

def pegar_posts():
    try:
        resposta = requests.get(SITE_URL, timeout=10)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print("Erro ao acessar o site")
            return []
    except:
        return []

def extrair_link(post):
    try:
        return post["jetpack_featured_media_url"]
    except:
        return None

def publicar(canal_id, caminho_video, legenda):
    try:
        with open(caminho_video, "rb") as video:
            bot.send_video(chat_id=canal_id, video=video, caption=legenda)
        print(f"Publicado em {canal_id}")
    except TelegramError as e:
        print(f"Erro ao publicar: {e}")

def main():
    print("Bot iniciado...")
    posts_ja_postados = set()

    while True:
        posts = pegar_posts()

        for post in posts:
            link_video = extrair_link(post)
            if not link_video or link_video in posts_ja_postados:
                continue

            nome_arquivo = "video.mp4"
            legenda = post["title"]["rendered"]

            if baixar_video(link_video, nome_arquivo):
                publicar(CANAL_1_ID, nome_arquivo, legenda)

                # Espera 24 horas antes de postar no segundo canal
                time.sleep(5)  # coloque 86400 para 24h reais
                publicar(CANAL_2_ID, nome_arquivo, legenda)

                posts_ja_postados.add(link_video)
                os.remove(nome_arquivo)

        time.sleep(1800)  # espera 30 minutos antes de verificar novamente

if __name__ == "__main__":
    main()
