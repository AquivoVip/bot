import os
import logging
import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Carrega variáveis do ambiente
load_dotenv()
TOKEN = os.getenv("TOKEN")
CANAL_PRINCIPAL = os.getenv("CANAL_PRINCIPAL")
CANAL_SECUNDARIO = os.getenv("CANAL_SECUNDARIO")

# Logger configurado
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Controlador de links
ULTIMO_LINK = None

async def buscar_video_novo():
    global ULTIMO_LINK
    url = "https://fxggxt.com"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            html = await resposta.text()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".gridItem")

            for card in cards:
                link_tag = card.find("a")
                if not link_tag:
                    continue
                link = "https://fxggxt.com" + link_tag["href"]
                if link == ULTIMO_LINK:
                    break

                ULTIMO_LINK = link
                titulo = link_tag.get("title", "Novo vídeo")

                img_tag = card.find("img")
                img_url = img_tag["src"] if img_tag else None

                nomes_modelos = extrair_modelos(titulo)
                legenda_img = f"{titulo}\nOnlyFans – {nomes_modelos}\n\n🦋 @ArquivoVIPcentral 🔞"
                legenda_video = "⎯ @ComboCompletoBot"

                if img_url:
                    await postar_conteudo(img_url, link, legenda_img, legenda_video)
                break

def extrair_modelos(titulo):
    nomes = re.findall(r"–\s(.+)", titulo)
    return nomes[0] if nomes else "Modelos desconhecidos"

async def postar_conteudo(img_url, video_url, legenda_img, legenda_video):
    bot = Bot(token=TOKEN)
    try:
        await bot.send_photo(chat_id=CANAL_PRINCIPAL, photo=img_url, caption=legenda_img, parse_mode=ParseMode.HTML)
        await asyncio.sleep(86400)
        await bot.send_video(chat_id=CANAL_SECUNDARIO, video=video_url, caption=legenda_video, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Erro ao enviar conteúdo: {e}")

async def iniciar_monitoramento():
    while True:
        try:
            await buscar_video_novo()
        except Exception as e:
            logging.error(f"Erro no monitoramento: {e}")
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(iniciar_monitoramento())
