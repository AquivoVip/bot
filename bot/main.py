import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re
import logging
import time

load_dotenv()

TOKEN = os.getenv("TOKEN")
CANAL_PRINCIPAL = os.getenv("CANAL_PRINCIPAL")
CANAL_SECUNDARIO = os.getenv("CANAL_SECUNDARIO")

bot = Bot(token=TOKEN)

# Armazena vídeos já postados
postados = set()

# Padrão de identificação da thumb e título
def extrair_info(soup):
    try:
        primeiro = soup.select_one("div.grid > a")
        if not primeiro:
            return None

        link = "https://fxggxt.com" + primeiro.get("href")
        titulo = primeiro.select_one("div.content h3").text.strip()
        modelos = primeiro.select_one("div.content span").text.strip()
        img_url = primeiro.select_one("img").get("data-src")

        return {
            "link": link,
            "titulo": titulo,
            "modelos": modelos,
            "img_url": img_url
        }
    except Exception as e:
        print("Erro ao extrair info:", e)
        return None

# Função principal
async def monitorar_site():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://fxggxt.com/") as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    dados = extrair_info(soup)

                    if dados and dados["link"] not in postados:
                        postados.add(dados["link"])
                        print(f"Novo conteúdo: {dados['titulo']}")

                        # Baixa a imagem
                        async with session.get(dados["img_url"]) as img_resp:
                            img_bytes = await img_resp.read()

                        # Envia a imagem com legenda no canal principal
                        legenda = f"{dados['titulo']}\nOnlyFans – {dados['modelos']}\n\n🦋 @ArquivoVIPcentral 🔞"
                        await bot.send_photo(
                            chat_id=CANAL_PRINCIPAL,
                            photo=img_bytes,
                            caption=legenda,
                            parse_mode=ParseMode.HTML
                        )

                        # Espera alguns segundos e baixa o vídeo
                        async with session.get(dados["link"]) as video_page:
                            html_video = await video_page.text()
                            soup_video = BeautifulSoup(html_video, "html.parser")
                            source = soup_video.select_one("video source")
                            if source:
                                video_url = source.get("src")

                                async with session.get(video_url) as video_resp:
                                    video_bytes = await video_resp.read()

                                # Espera 24 horas para postar no canal secundário
                                await asyncio.sleep(86400)  # 24h = 86400s

                                await bot.send_video(
                                    chat_id=CANAL_SECUNDARIO,
                                    video=video_bytes,
                                    caption="⎯ @ComboCompletoBot"
                                )

        except Exception as e:
            logging.error(f"Erro no monitoramento: {e}")

        await asyncio.sleep(300)  # Espera 5 minutos para verificar novamente

if __name__ == "__main__":
    asyncio.run(monitorar_site())
