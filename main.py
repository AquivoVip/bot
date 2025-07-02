import os
import time
import asyncio
import aiohttp
from datetime import datetime
from telegram import Bot
from bs4 import BeautifulSoup
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis do ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_1_ID = int(os.getenv("CANAL_1_ID"))
CANAL_2_ID = int(os.getenv("CANAL_2_ID"))

bot = Bot(token=BOT_TOKEN)

# Configurações
URL_SITE = "https://fxggxt.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
INTERVALO = 600  # 10 min
HORAS_ATIVAS = list(range(13, 24)) + list(range(0, 5))
HISTORICO = set()

async def baixar(session, url, caminho):
    try:
        async with session.get(url) as r:
            if r.status == 200:
                with open(caminho, 'wb') as f:
                    f.write(await r.read())
                return True
    except Exception as e:
        logger.error(f"Erro ao baixar {url}: {e}")
    return False

async def extrair_videos():
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as s:
            async with s.get(URL_SITE) as r:
                html = await r.text()
                soup = BeautifulSoup(html, 'html.parser')
                return [
                    a['href'] for a in soup.find_all('a', href=True)
                    if '/video/' in a['href'] and a['href'] not in HISTORICO
                ]
    except Exception as e:
        logger.error(f"Erro ao extrair vídeos: {e}")
        return []

async def postar_video(video_url):
    try:
        titulo = video_url.split('/')[-1].replace('-', ' ').replace('.html', '').title()
        url_completo = f"{URL_SITE.rstrip('/')}{video_url}"
        thumb_path = f"thumb_{int(time.time())}.jpg"
        video_path = f"video_{int(time.time())}.mp4"

        async with aiohttp.ClientSession(headers=HEADERS) as s:
            async with s.get(url_completo) as r:
                html = await r.text()
                try:
                    thumb = html.split('poster="')[1].split('"')[0]
                    video = html.split('src="')[1].split('"')[0]
                except:
                    return

                if not await baixar(s, thumb, thumb_path): return
                if not await baixar(s, video, video_path): return

        # CANAL 1
        await bot.send_photo(chat_id=CANAL_1_ID, photo=open(thumb_path, 'rb'), caption=titulo)
        await asyncio.sleep(180)
        await bot.send_video(chat_id=CANAL_1_ID, video=open(video_path, 'rb'))

        # CANAL 2 (24h depois)
        await asyncio.sleep(86400 - 180)
        await bot.send_photo(chat_id=CANAL_2_ID, photo=open(thumb_path, 'rb'), caption=f"{titulo}\n▬▬▬▬▬▬▬▬▬▬▬▬▬\n🦋 @ArquivoVIPcentral 🔞")
        await asyncio.sleep(180)
        await bot.send_video(chat_id=CANAL_2_ID, video=open(video_path, 'rb'), caption="💳  @ComboCompletoBot")

        HISTORICO.add(video_url)
        os.remove(thumb_path)
        os.remove(video_path)

    except Exception as e:
        logger.error(f"Erro ao postar {video_url}: {e}")

async def executar():
    while True:
        hora = datetime.now().hour
        if hora in HORAS_ATIVAS:
            novos = await extrair_videos()
            for url in novos:
                await postar_video(url)
        await asyncio.sleep(INTERVALO)

if __name__ == '__main__':
    asyncio.run(executar())
