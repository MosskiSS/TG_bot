from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Словарь для хранения данных пользователей временно
user_data = {}

# Функция /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Поехали! 🥳", callback_data="start_application")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Здравствуйте! 😉\n\nВас приветствует администрация сервера \"Mistery World\".\n\nДля запуска, нажмите кнопку ниже.",
        reply_markup=reply_markup
    )

# Функция обработки кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Обработка нажатий на кнопки
    if query.data == "start_application":
        await query.edit_message_text("Вы находитесь в главном меню. Выберите ниже, что хотите сделать.\n\nЕсли вы хотите начать играть на сервере, выбирайте кнопку \"Заявка\".")
        keyboard = [[InlineKeyboardButton("Заявка", callback_data="application")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Нажмите кнопку ниже, чтобы начать заполнение заявки.", reply_markup=reply_markup)

    elif query.data == "application":
        user_data[query.from_user.id] = {}  # Создаем запись для пользователя
        await query.message.reply_text("Вы выбрали раздел заявка\n\nВаш NickName?")
        context.user_data['state'] = 'nickname'

# Функция обработки ответов на вопросы
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = context.user_data.get('state')

    # Обрабатываем каждый этап заявки
    if state == 'nickname':
        user_data[user_id]['nickname'] = update.message.text
        await update.message.reply_text("Сколько вам лет?")
        context.user_data['state'] = 'age'
    elif state == 'age':
        user_data[user_id]['age'] = update.message.text
        await update.message.reply_text("На какой платформе играете? (Java / Bedrock)")
        context.user_data['state'] = 'platform'
    elif state == 'platform':
        user_data[user_id]['platform'] = update.message.text
        await update.message.reply_text("Откуда узнали о нас?")
        context.user_data['state'] = 'source'
    elif state == 'source':
        user_data[user_id]['source'] = update.message.text
        await update.message.reply_text("Соглашаетесь соблюдать правила сервера?")
        context.user_data['state'] = 'agreement'
    elif state == 'agreement':
        user_data[user_id]['agreement'] = update.message.text
        await update.message.reply_text("Вы успешно написали заявку! 😄\n\nВ течении 10 часов мы рассмотрим её и вынесем вердикт.")
        
        # Отправляем заявку в чат с администрацией
        await send_application_to_admin(context, user_id, update.message.from_user.username)

        # Сбрасываем состояние пользователя
        context.user_data['state'] = None
        user_data.pop(user_id, None)

async def send_application_to_admin(context, user_id, username):
    application = user_data[user_id]
    admin_message = (
        f"Поступила новая заявка!\n\n"
        f"Телеграм данные:\n(@{username})\n\n"
        f"Данные пользователя:\n"
        f"1. Никнейм: {application['nickname']}\n"
        f"2. Годиков: {application['age']}\n"
        f"3. Платформа: {application['platform']}\n"
        f"4. Узнал: {application['source']}\n"
        f"5. Согласие: {application['agreement']}\n\n"
        "@MoskI_I @moidar5366"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

# Основная функция запуска бота
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
