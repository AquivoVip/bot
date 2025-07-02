from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging

# TOKEN DIRETO (você autorizou usar assim para testes)
TOKEN = "7859249744:AAEBSoSq0w_u_y2sVdIKnNs4l40VJrNsCZKU"

# Configurar o log para facilitar depuração
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Função de resposta ao comando /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Olá! Eu sou o seu bot, pronto para funcionar!")

# Função principal que inicializa o bot
def main():
    # Cria o bot e o updater
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Adiciona o comando /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Inicia o bot
    updater.start_polling()
    updater.idle()

# Executa o bot
if __name__ == '__main__':
    main()
