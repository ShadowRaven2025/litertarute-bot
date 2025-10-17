# render_bot.py - для Render.com
import logging
import os
import random
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = "8421692900:AAH8-5L37_6SeNYKQ_RwsUJbva-kV71F8QU"

# Автоматическое определение URL
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"
else:
    # Если запускаем локально
    WEBHOOK_URL = None

app = Flask(__name__)

# База книг
BOOKS_DATABASE = [
    {
        "id": 1,
        "title": "Хоббит, или Туда и обратно",
        "author": "Дж. Р. Р. Толкин", 
        "genres": ["Фэнтези", "Приключения"],
        "description": "Классическая история о путешествии Бильбо Бэггинса."
    },
    {
        "id": 2,
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "genres": ["Классика", "Мистика", "Сатира"],
        "description": "Мистический роман о визите дьявола в Москву 1930-х годов."
    },
    {
        "id": 3, 
        "title": "1984",
        "author": "Джордж Оруэлл",
        "genres": ["Антиутопия", "Научная фантастика"],
        "description": "Роман-антиутопия о тоталитарном обществе под постоянным контролем."
    }
]

class BookBot:
    def __init__(self):
        self.user_states = {}
        
    def handle_start(self, user_id: int, user_name: str = "") -> str:
        self.user_states[user_id] = {"step": "start"}
        return (
            "📚 *Добро пожаловать в Литературный Гурман!*\n\n"
            "Я помогу подобрать тебе книгу для чтения.\n\n"
            "*Команды:*\n"
            "/start - начать\n" 
            "/recommend - подобрать книгу\n"
            "/books - список книг\n"
            "/help - помощь"
        )
    
    def handle_recommend(self, user_id: int) -> str:
        book = random.choice(BOOKS_DATABASE)
        return (
            f"📖 *{book['title']}*\n"
            f"✍️ *Автор:* {book['author']}\n"
            f"🏷️ *Жанры:* {', '.join(book['genres'])}\n"
            f"📝 *Описание:* {book['description']}\n\n"
            "Приятного чтения! 📚"
        )
    
    def handle_books(self, user_id: int) -> str:
        response = "📖 *Все книги:*\n\n"
        for i, book in enumerate(BOOKS_DATABASE, 1):
            response += f"{i}. *{book['title']}* - {book['author']}\n"
        return response

# Создаем экземпляр бота
book_bot = BookBot()

# Инициализация приложения Telegram
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Обработчики команд
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or ""
    response = book_bot.handle_start(user_id, user_name)
    await update.message.reply_text(response, parse_mode='Markdown')

async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    response = book_bot.handle_recommend(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def books_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    response = book_bot.handle_books(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Помощь*\n\n"
        "/start - начать\n"
        "/recommend - случайная книга\n"
        "/books - список книг",
        parse_mode='Markdown'
    )

# Добавляем обработчики
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("recommend", recommend_command))
application.add_handler(CommandHandler("books", books_command))
application.add_handler(CommandHandler("help", help_command))

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Обработчик вебхука от Telegram"""
    try:
        json_data = request.get_json()
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return 'ok'
    except Exception as e:
        logger.error(f"Ошибка в вебхуке: {e}")
        return 'error'

@app.route('/')
def home():
    return "📚 Книжный бот работает на Render.com!"

@app.route('/set_webhook')
def set_webhook():
    """Установка вебхука"""
    try:
        if WEBHOOK_URL:
            application.bot.set_webhook(WEBHOOK_URL)
            return f"✅ Вебхук установлен: {WEBHOOK_URL}"
        else:
            return "❌ WEBHOOK_URL не определен"
    except Exception as e:
        return f"❌ Ошибка установки вебхука: {e}"

@app.route('/remove_webhook')
def remove_webhook():
    """Удаление вебхука"""
    try:
        application.bot.delete_webhook()
        return "✅ Вебхук удален"
    except Exception as e:
        return f"❌ Ошибка удаления вебхука: {e}"

def main():
    """Запуск приложения"""
    port = int(os.environ.get('PORT', 10000))
    
    # Устанавливаем вебхук при запуске
    if WEBHOOK_URL:
        logger.info(f"Устанавливаем вебхук: {WEBHOOK_URL}")
        application.bot.set_webhook(WEBHOOK_URL)
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()

