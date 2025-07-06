import os
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv

# Carregar variáveis de ambiente da Railway
load_dotenv()
TOKEN = os.getenv("TOKEN")
CANAL_PRINCIPAL = os.getenv("CANAL_PRINCIPAL")
CANAL_SECUNDARIO = os.getenv("CANAL_SECUNDARIO")

# Ativar logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Instanciar o bot global
bot = Bot(token=TOKEN)

# Variável para controlar últimos links postados
ULTIMO_LINK = None

# Função para buscar os vídeos do site
async def buscar_videos_novos():
    global ULTIMO_LINK
    url = "https://fxggxt.com"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            html = await resposta.text()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".gridItem")

            for card in cards:
                link_tag = card.find("a")
                if link_tag:
                    link = "https://fxggxt.com" + link_tag["href"]
                    if link != ULTIMO_LINK:
                        ULTIMO_LINK = link
                        titulo = link_tag.get("title", "Novo vídeo")

                        # Baixa a imagem de capa
                        img_tag = card.find("img")
                        if img_tag and img_tag.get("src"):
                            img_url = img_tag["src"]
                            await enviar_para_canais(titulo, link, img_url)
                    break  # Envia apenas o vídeo mais recente

# Envia o vídeo para os canais
async def enviar_para_canais(titulo, link, img_url):
    legenda = f"🔥 {titulo}\n\n🔗 {link}"

    try:
        # Enviar para o canal principal agora
        await bot.send_photo(chat_id=CANAL_PRINCIPAL, photo=img_url, caption=legenda)
        logging.info("Enviado ao canal principal com sucesso.")

        # Aguardar 24 horas e enviar para o canal secundário
        await asyncio.sleep(86400)
        await bot.send_photo(chat_id=CANAL_SECUNDARIO, photo=img_url, caption=legenda)
        logging.info("Enviado ao canal secundário com sucesso.")

    except Exception as e:
        logging.error(f"Erro ao enviar para os canais: {e}")

# Loop contínuo que verifica novos vídeos a cada 5 minutos
async def monitorar_site():
    while True:
        try:
            await buscar_videos_novos()
        except Exception as e:
            logging.error(f"Erro no monitoramento: {e}")
        await asyncio.sleep(300)  # Espera 5 minutos

# Iniciar o monitoramento
if __name__ == "__main__":
    asyncio.run(monitorar_site())
