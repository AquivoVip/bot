import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CANAL_1_ID = os.getenv("CANAL_1_ID")
CANAL_2_ID = os.getenv("CANAL_2_ID")

# Ativar logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ O bot está funcionando!")

# Função principal
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("✅ Bot iniciado com sucesso!")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
