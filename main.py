import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import os
from dotenv import load_dotenv
# Загружаем переменные из .env файла
load_dotenv()

# Настройка логирования
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# Конфигурация бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_LINK = os.getenv('CHANNEL_LINK')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
YANDEX_DISK_LINK = os.getenv('YANDEX_DISK_LINK')
FILE_PATH = os.getenv('FILE_PATH', 'materials.pdf')
PROCESSING_LINK = os.getenv("PROCESSING_LINK")
POLITICS_LINK = os.getenv("POLITICS_LINK")

# Создаем клавиатуры
consent_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Согласен", callback_data="consent")]
])

get_material_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Забрать подарок 🎁", callback_data="get_material")]
])

check_subscription_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    text = (
        "👋 Добро пожаловать!\n\n"
        "Вас приветствует бот-помощник Татьяны Ручкиной.\n\n"
        "Для продолжения работы и получения доступа к материалам необходимо нажать на кнопку ниже.\n\n"
        "Этим действием вы подтверждаете <a href='{process_link}'>свое согласие на обработку персональных данных</a> в соответствии с <a href='{politics_link}'>Политикой обработки персональных данных</a>\n\n"
        "Нажмите на кнопку 👇"
    ).format(process_link=PROCESSING_LINK, politics_link=POLITICS_LINK)
    
    await update.message.reply_text(
        text, 
        reply_markup=consent_keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "consent":
        text = (
            
            "📋 ИНСТРУКЦИЯ: как получить подарок\n\n"
            "1️⃣ Перейдите в канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a>:\n"
            "и нажмите кнопку «Подписаться».\n"
            "2️⃣ Вернитесь в этот чат-бот и нажмите «Забрать подарок 🎁».\n\n"
            "💫 Сразу после этого вы мгновенно получите доступ к материалу\n"
            "«Как пройти правильный чек-ап после 40».\n"
        ).format(channel_link=CHANNEL_LINK)
        await query.message.reply_text(
            text, 
            reply_markup=get_material_keyboard, 
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    
    elif query.data == "get_material":
        user_id = query.from_user.id
        # await context.bot.send_photo(chat_id=user_id, photo=open("Pro.jpg","rb"))
        print('---------------')
        # Проверяем подписку на канал
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=CHANNEL_USERNAME, 
                user_id=user_id
            )
            print(chat_member)
            # Статусы, которые считаются подпиской
            valid_statuses = ["member", "administrator", "creator"]
            
            if chat_member.status in valid_statuses:
                # Пользователь подписан - выдаем материал
                text = (
                    "🎉 Поздравляем! Вы получили доступ к подарку!\n\n"
                    "Материал загружается, ожидайте...\n"
                    
                )
                await query.message.reply_text(
                    text, 
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                with open(FILE_PATH, "rb") as file:
                    await query.message.reply_document(
                        document=file,
                        caption="📁 Скачайте подарок\n"
                    )
            else:
                # Пользователь не подписан
                text = (
                    "❌ Вы не подписаны на канал!\n\n"
                    "Пожалуйста, подпишитесь на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и нажмите кнопку ниже для проверки."
                ).format(channel_link=CHANNEL_LINK)
                await query.message.reply_text(
                    text,
                    reply_markup=check_subscription_keyboard,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                
        except Exception as e:
            # Если бот не может проверить подписку (не добавлен в канал как администратор)
            logging.error(f"Ошибка проверки подписки: {e}")
            text = (
                "⚠️ Не могу проверить подписку.\n\n"
                "Пожалуйста, убедитесь что подписались на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и нажмите кнопку ниже.\n\n"
                "<i>Если проблема повторяется, администратору нужно добавить бота в канал как администратора.</i>"
            ).format(channel_link=CHANNEL_LINK)
            await query.message.reply_text(
                text,
                reply_markup=check_subscription_keyboard,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
    
    elif query.data == "check_subscription":
        user_id = query.from_user.id
        
        # Повторная проверка подписки
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=CHANNEL_USERNAME, 
                user_id=user_id
            )
            print(chat_member)
            
            valid_statuses = ["member", "administrator", "creator"]
            
            if chat_member.status in valid_statuses:
                text = (
                    "🎉 Отлично! Теперь вы подписаны на канал!\n\n"
                    "📁 Скачайте материал по ссылке:\n"
                    "<a href='{disk_link}'>Яндекс.Диск с материалами</a>\n\n"
                    "Если возникли проблемы со скачиванием, напишите в поддержку."
                ).format(disk_link=YANDEX_DISK_LINK)
                await query.message.reply_text(
                    text, 
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            else:
                text = (
                    "❌ Вы все еще не подписаны на канал!\n\n"
                    "Пожалуйста, подпишитесь на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и нажмите кнопку ниже для проверки."
                ).format(channel_link=CHANNEL_LINK)
                # Для редактирования сообщения с кнопкой используем edit_message_text у query
                await query.edit_message_text(
                    text,
                    reply_markup=check_subscription_keyboard,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                
        except Exception as e:
            logging.error(f"Ошибка проверки подписки: {e}")
            text = (
                "⚠️ Все еще не могу проверить подписку.\n\n"
                "Пожалуйста, убедитесь что подписались на канал <a href='{channel_link}'>Энергия и стройность с Татьяной Ручкиной</a> и попробуйте снова."
            ).format(channel_link=CHANNEL_LINK)
            await query.edit_message_text(
                text,
                reply_markup=check_subscription_keyboard,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )


def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    print("Бот запущен! Для остановки нажмите Ctrl+C")
    application.run_polling()

if __name__ == "__main__":
    main()