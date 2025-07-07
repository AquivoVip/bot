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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("TOKEN")
CANAL_PRINCIPAL = os.getenv("CANAL_PRINCIPAL")
CANAL_SECUNDARIO = os.getenv("CANAL_SECUNDARIO")

# Validar variáveis de ambiente
if not TOKEN or not CANAL_PRINCIPAL or not CANAL_SECUNDARIO:
    raise ValueError("Variáveis de ambiente TOKEN, CANAL_PRINCIPAL e CANAL_SECUNDARIO devem estar definidas")

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
        
        # Verificar se os elementos existem antes de acessar
        titulo_elem = primeiro.select_one("div.content h3")
        modelos_elem = primeiro.select_one("div.content span")
        img_elem = primeiro.select_one("img")
        
        if not titulo_elem or not modelos_elem or not img_elem:
            logger.warning("Elementos necessários não encontrados na página")
            return None
        
        titulo = titulo_elem.text.strip()
        modelos = modelos_elem.text.strip()
        img_url = img_elem.get("data-src") or img_elem.get("src")
        
        return {
            "link": link,
            "titulo": titulo,
            "modelos": modelos,
            "img_url": img_url
        }
    except Exception as e:
        logger.error(f"Erro ao extrair info: {e}")
        return None

# Função para processar vídeo com delay
async def processar_video_com_delay(session, dados):
    """Processa o vídeo e agenda o envio para o canal secundário"""
    try:
        # Baixa a página do vídeo
        async with session.get(dados["link"]) as video_page:
            html_video = await video_page.text()
            soup_video = BeautifulSoup(html_video, "html.parser")
            source = soup_video.select_one("video source")
            
            if source:
                video_url = source.get("src")
                if video_url:
                    # Se a URL for relativa, torna absoluta
                    if video_url.startswith("/"):
                        video_url = "https://fxggxt.com" + video_url
                    
                    logger.info(f"Aguardando 24 horas para postar vídeo: {dados['titulo']}")
                    await asyncio.sleep(86400)  # 24h = 86400s
                    
                    # Baixa e envia o vídeo
                    async with session.get(video_url) as video_resp:
                        if video_resp.status == 200:
                            video_bytes = await video_resp.read()
                            await bot.send_video(
                                chat_id=CANAL_SECUNDARIO,
                                video=video_bytes,
                                caption="⎯ @ComboCompletoBot"
                            )
                            logger.info(f"Vídeo enviado para canal secundário: {dados['titulo']}")
                        else:
                            logger.error(f"Erro ao baixar vídeo: Status {video_resp.status}")
                else:
                    logger.warning("URL do vídeo não encontrada")
            else:
                logger.warning("Elemento de vídeo não encontrado na página")
                
    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {e}")

# Função principal
async def monitorar_site():
    logger.info("Iniciando monitoramento do site...")
    
    while True:
        try:
            # Configurar timeout e headers para evitar bloqueios
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get("https://fxggxt.com/") as resp:
                    if resp.status != 200:
                        logger.error(f"Erro ao acessar site: Status {resp.status}")
                        continue
                        
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    dados = extrair_info(soup)
                    
                    if dados and dados["link"] not in postados:
                        postados.add(dados["link"])
                        logger.info(f"Novo conteúdo encontrado: {dados['titulo']}")
                        
                        # Baixa a imagem
                        try:
                            async with session.get(dados["img_url"]) as img_resp:
                                if img_resp.status == 200:
                                    img_bytes = await img_resp.read()
                                    
                                    # Envia a imagem com legenda no canal principal
                                    legenda = f"{dados['titulo']}\nOnlyFans – {dados['modelos']}\n\n🦋 @ArquivoVIPcentral 🔞"
                                    await bot.send_photo(
                                        chat_id=CANAL_PRINCIPAL,
                                        photo=img_bytes,
                                        caption=legenda,
                                        parse_mode=ParseMode.HTML
                                    )
                                    logger.info(f"Imagem enviada para canal principal: {dados['titulo']}")
                                    
                                    # Inicia o processamento do vídeo em background
                                    asyncio.create_task(processar_video_com_delay(session, dados))
                                    
                                else:
                                    logger.error(f"Erro ao baixar imagem: Status {img_resp.status}")
                        except Exception as e:
                            logger.error(f"Erro ao processar imagem: {e}")
                            
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
            
        # Espera 5 minutos para verificar novamente
        await asyncio.sleep(300)

if __name__ == "__main__":
    try:
        asyncio.run(monitorar_site())
    except KeyboardInterrupt:
        logger.info("Monitoramento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
