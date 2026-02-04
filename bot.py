from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os

TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise ValueError("Переменная окружения TOKEN не найдена!")



# Специалист (бот сам запомнит после первого сообщения)
SPECIALIST_CHAT_ID = 1347805920

# Храним обращения пользователей
pending_requests = {}

# ====== КУРСЫ ======
courses_list = [
    "Основы работы с мобильным телефоном",
    "Работа с электронной почтой",
    "Безопасность в сети интернет",
    "Использование социальных сетей",
    "Приложения для здоровья и фитнеса",
    "Цифровая фотография и обработка снимков",
    "Практическое занятие музыкой и искусством онлайн",
    "Посещение виртуальных музеев и театров"
]

# ====== ГЛАВНОЕ МЕНЮ ======
main_menu = ReplyKeyboardMarkup(
    [
        ["📚 Мои курсы", "🌐 Помощь по сайту"],
        ["❓ Задать вопрос", "📷 Отправить фото"],
        ["🆘 Поддержка"]
    ],
    resize_keyboard=True
)


# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте 😊\n"
        "Я помощник для обучения.\n"
        "Я помогу вам разобраться с курсами и сайтом.\n\n"
        "Выберите, чем я могу помочь:",
        reply_markup=main_menu
    )


# ====== МОИ КУРСЫ ======
async def show_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📚 Вот курсы, которые вам доступны:\n\n"

    for course in courses_list:
        text += f"• {course}\n"

    text += "\nЧтобы узнать подробнее — напишите название курса 😊"

    await update.message.reply_text(text)


# ====== ПОМОЩЬ ПО САЙТУ ======
async def site_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 Добро пожаловать в OldSchool-NewTools!\n\n"
        "Это пространство, где мудрость поколений встречается "
        "с возможностями современных технологий.\n\n"
        "Мы помогаем людям старшего поколения:\n"
        "✅ понять смартфон\n"
        "✅ научиться пользоваться интернетом\n"
        "✅ общаться с близкими\n"
        "✅ слушать музыку, смотреть фото и видео\n"
        "✅ чувствовать себя уверенно и безопасно онлайн\n\n"
        "Если вам нужна помощь — напишите в поддержку 😊"
    )


# ====== ОТПРАВКА СПЕЦИАЛИСТУ ======
async def send_to_specialist(user_id, user_text, context, request_type):
    global SPECIALIST_CHAT_ID

    if not SPECIALIST_CHAT_ID:
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ Специалист пока не подключён.\n"
                 "Попросите @dendrocul написать боту любое сообщение."
        )
        return

    pending_requests[user_id] = request_type

    await context.bot.send_message(
        chat_id=SPECIALIST_CHAT_ID,
        text=
        f"🆘 Новое обращение!\n\n"
        f"Тип: {request_type}\n"
        f"Пользователь ID: {user_id}\n\n"
        f"Сообщение:\n{user_text}\n\n"
        f"Ответьте командой:\n"
        f"/reply {user_id} ваш ответ"
    )


# ====== ЗАДАТЬ ВОПРОС ======
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "question"
    await update.message.reply_text(
        "❓ Напишите ваш вопрос.\n"
        "Я передам его специалисту, чтобы вам помогли 😊"
    )


# ====== ОТПРАВИТЬ ФОТО ======
async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "photo"
    await update.message.reply_text(
        "📷 Прикрепите фото экрана.\n"
        "Специалист посмотрит и подскажет, что делать дальше 😊"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    await update.message.reply_text(
        "Фото получено ✅\n"
        "Я отправляю его специалисту. Ожидайте ответа 😊"
    )

    await context.bot.send_message(
        chat_id=SPECIALIST_CHAT_ID,
        text=f"📷 Пользователь {user_id} отправил фото.\n"
             f"Ответьте командой:\n/reply {user_id} ваш ответ"
    )


# ====== ПОДДЕРЖКА ======
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "support"
    await update.message.reply_text(
        "🆘 Опишите вашу проблему простыми словами.\n"
        "Я передам сообщение специалисту 😊"
    )


# ====== ОБРАБОТКА ТЕКСТА ======
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SPECIALIST_CHAT_ID

    text = update.message.text
    user_id = update.message.chat_id

    # Если специалист написал боту впервые
    if text.lower().startswith("специалист"):
        SPECIALIST_CHAT_ID = user_id
        await update.message.reply_text("✅ Вы назначены специалистом!")
        return

    # Главное меню
    if text == "📚 Мои курсы":
        await show_courses(update, context)
        return

    if text == "🌐 Помощь по сайту":
        await site_help(update, context)
        return

    if text == "❓ Задать вопрос":
        await ask_question(update, context)
        return

    if text == "📷 Отправить фото":
        await ask_photo(update, context)
        return

    if text == "🆘 Поддержка":
        await support(update, context)
        return

    # Если пользователь пишет вопрос
    mode = context.user_data.get("mode")

    if mode == "question":
        context.user_data["mode"] = None
        await update.message.reply_text(
            "Спасибо 😊 Я отправил ваш вопрос специалисту."
        )
        await send_to_specialist(user_id, text, context, "Вопрос")
        return

    if mode == "support":
        context.user_data["mode"] = None
        await update.message.reply_text(
            "Спасибо 😊 Сообщение отправлено в поддержку."
        )
        await send_to_specialist(user_id, text, context, "Поддержка")
        return

    # Если написали название курса
    if text in courses_list:
        await update.message.reply_text(
            f"📚 Вы выбрали курс:\n{text}\n\n"
            "Этот курс поможет вам шаг за шагом разобраться.\n"
            "Если хотите начать — напишите в поддержку 😊"
        )
        return

    # Если непонятно что написали
    await update.message.reply_text(
        "Я вас понял 😊\n"
        "Вы можете выбрать кнопку в меню или написать в поддержку."
    )


# ====== ОТВЕТ СПЕЦИАЛИСТА ======
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Используйте:\n/reply user_id ответ")
        return

    user_id = int(context.args[0])
    answer = " ".join(context.args[1:])

    await context.bot.send_message(
        chat_id=user_id,
        text=f"💬 Ответ специалиста:\n\n{answer}"
    )

    await update.message.reply_text("✅ Ответ отправлен пользователю.")


# ====== MAIN ======
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
