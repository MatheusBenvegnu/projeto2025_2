import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from flask import Flask, request

# Configuração do Flask
app = Flask(__name__)

# Token do Telegram (use variável de ambiente no servidor)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7843407309:AAEseTiJZm9FCxatdERmHJJTRCL7IZ8wIBw")
WEBHOOK_URL = "https://SEU_DOMINIO/render.com/webhook"  # Substitua pelo seu domínio no Render

# Teclado com opções
menu_principal = [['Realizar um novo pedido'], ['Acompanhar pedido'], ['Fazer sugestão ou reclamação']]
menu_pedido = [['Solicitar um site'], ['Solicitar equipe de suporte'], ['Solicitar serviços de rede']]

# Inicialização do bot
bot_app = Application.builder().token(TOKEN).build()

# Função de boas-vindas
async def start(update: Update, context: CallbackContext) -> None:
    teclado = ReplyKeyboardMarkup(menu_principal, resize_keyboard=True)
    await update.message.reply_text(
        "Olá! Seja bem-vindo ao ambiente virtual da Omolux Solutions.\nEscolha uma opção para ser atendido:",
        reply_markup=teclado
    )

# Função para gerenciar pedidos
async def pedido(update: Update, context: CallbackContext) -> None:
    teclado = ReplyKeyboardMarkup(menu_pedido, resize_keyboard=True)
    await update.message.reply_text("Selecione o tipo de pedido:", reply_markup=teclado)

# Função para tratar subopções de pedido
async def subpedido(update: Update, context: CallbackContext) -> None:
    opcao = update.message.text
    if opcao == "Solicitar um site":
        await update.message.reply_text("Por favor, envie um e-mail para contato@omoluxsolutions.com com os requisitos e solicite uma reunião online com o time.")
    elif opcao == "Solicitar equipe de suporte":
        await update.message.reply_text("Acesse nosso site e vá até a opção 'Suporte': [www.omoluxsolutions.com/suporte](https://www.omoluxsolutions.com/suporte)")
    elif opcao == "Solicitar serviços de rede":
        protocolo = "OMX-" + str(update.message.message_id)
        await update.message.reply_text(f"Aqui está seu protocolo de atendimento: {protocolo}. Agende uma reunião conosco!")

# Função para acompanhar pedido
async def acompanhar_pedido(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Por favor, envie seu protocolo de atendimento.")
    context.user_data["aguardando_protocolo"] = True

# Função para verificar protocolo
async def verificar_protocolo(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("aguardando_protocolo"):
        protocolo = update.message.text
        if protocolo.startswith("OMX-"):
            await update.message.reply_text("Protocolo identificado! Descreva o erro para darmos continuidade ao suporte.")
        else:
            await update.message.reply_text("Não conseguimos localizar seu cadastro.")
        context.user_data["aguardando_protocolo"] = False

# Função para sugestões ou reclamações
async def sugestao_reclamacao(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Por favor, envie sua sugestão ou reclamação. Nossa equipe analisará sua mensagem.")

# Configuração das rotas para Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe as requisições do Telegram e processa o bot."""
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.process_update(update)
    return "OK", 200

# Configuração do bot
def main():
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pedido))
    bot_app.add_handler(MessageHandler(filters.Regex("^(Solicitar um site|Solicitar equipe de suporte|Solicitar serviços de rede)$"), subpedido))
    bot_app.add_handler(MessageHandler(filters.Regex("^Acompanhar pedido$"), acompanhar_pedido))
    bot_app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^[A-Za-z0-9-]+$"), verificar_protocolo))
    bot_app.add_handler(MessageHandler(filters.Regex("^Fazer sugestão ou reclamação$"), sugestao_reclamacao))

    # Configura o webhook no Telegram
    bot_app.bot.set_webhook(url=WEBHOOK_URL)

if __name__ == '__main__':
    main()
    app.run(host="0.0.0.0", port=8080)
