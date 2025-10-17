import logging
import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Токен бота
TELEGRAM_BOT_TOKEN = "8421692900:AAH8-5L37_6SeNYKQ_RwsUJbva-kV71F8QU"

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
    },
    {
        "id": 4,
        "title": "Гарри Поттер и философский камень", 
        "author": "Джоан Роулинг",
        "genres": ["Фэнтези", "Приключения"],
        "description": "Первая книга о юном волшебнике Гарри Поттере."
    },
    {
        "id": 5,
        "title": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "genres": ["Классика", "Психологический роман"],
        "description": "История бывшего студента Родиона Раскольникова."
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
            "*Доступные команды:*\n"
            "/start - начать работу\n" 
            "/recommend - подобрать книгу\n"
            "/books - список всех книг\n"
            "/help - помощь\n\n"
            "Напиши */recommend* чтобы начать!"
        )
    
    def handle_recommend(self, user_id: int) -> str:
        self.user_states[user_id] = {"step": "asking_genre"}
        return (
            "Отлично! Давай подберем книгу.\n\n"
            "Напиши *один или несколько* жанров через запятую.\n"
            "Например: *Фэнтези, Детектив, Классика*\n\n"
            "*Доступные жанры:* Фэнтези, Классика, Приключения, Научная фантастика, Антиутопия, Мистика, Сатира, Психологический роман"
        )
    
    def handle_books(self, user_id: int) -> str:
        response = "📖 *Все книги в библиотеке:*\n\n"
        for i, book in enumerate(BOOKS_DATABASE, 1):
            response += f"{i}. *{book['title']}* - {book['author']}\n"
            response += f"   🏷️ {', '.join(book['genres'])}\n\n"
        return response
    
    def handle_help(self, user_id: int) -> str:
        return (
            "*📚 Литературный Гурман - Помощь*\n\n"
            "*Как пользоваться:*\n"
            "1. Напиши /recommend\n" 
            "2. Укажи любимые жанры\n"
            "3. Получи рекомендацию!\n\n"
            "*Команды:*\n"
            "/start - начать диалог\n"
            "/recommend - подобрать книгу\n" 
            "/books - список всех книг\n"
            "/help - эта справка\n\n"
            f"*В библиотеке:* {len(BOOKS_DATABASE)} книг"
        )
    
    def handle_message(self, user_id: int, user_input: str, user_name: str = "") -> str:
        user_input_lower = user_input.lower()
        
        # Обработка команд
        if user_input_lower in ("/start", "start", "начать"):
            return self.handle_start(user_id, user_name)
        elif user_input_lower in ("/recommend", "recommend", "подобрать"):
            return self.handle_recommend(user_id)
        elif user_input_lower in ("/books", "books", "книги"):
            return self.handle_books(user_id)
        elif user_input_lower in ("/help", "help", "помощь"):
            return self.handle_help(user_id)
        
        # Обработка диалога
        user_state = self.user_states.get(user_id, {"step": "start"})
        
        if user_state["step"] == "asking_genre":
            # Сохраняем жанры и рекомендуем книгу
            genres = [genre.strip() for genre in user_input.split(",")]
            user_state["genres"] = genres
            user_state["step"] = "done"
            
            # Подбираем книгу
            filtered_books = []
            for book in BOOKS_DATABASE:
                book_genres_lower = [g.lower() for g in book["genres"]]
                user_genres_lower = [g.lower() for g in genres]
                if any(genre in book_genres_lower for genre in user_genres_lower):
                    filtered_books.append(book)
            
            if not filtered_books:
                filtered_books = BOOKS_DATABASE
                message = "К сожалению, нет книг в этих жанрах. Вот случайная рекомендация:\n\n"
            else:
                message = "Вот что я подобрал для тебя:\n\n"
            
            book = random.choice(filtered_books)
            
            return (
                f"{message}"
                f"📖 *{book['title']}*\n"
                f"✍️ *Автор:* {book['author']}\n"
                f"🏷️ *Жанры:* {', '.join(book['genres'])}\n"
                f"📝 *Описание:* {book['description']}\n\n"
                "Приятного чтения! 📚\n\n"
                "Хочешь еще книгу? Напиши */recommend*"
            )
        
        return (
            "Я не совсем понимаю. 😕\n\n"
            "Напиши */recommend* чтобы подобрать книгу\n"
            "или */help* для справки."
        )

# Создаем экземпляр бота
book_bot = BookBot()

# Обработчики для Telegram
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
    user_id = update.effective_user.id
    response = book_bot.handle_help(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    user_name = update.effective_user.first_name or ""
    response = book_bot.handle_message(user_id, user_input, user_name)
    await update.message.reply_text(response, parse_mode='Markdown')

async def main():
    print("🚀 Запуск бота на Render.com...")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("recommend", recommend_command))
    application.add_handler(CommandHandler("books", books_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    
    # Запускаем бота с polling
    print("✅ Бот запущен! Используется polling...")
    await application.run_polling()

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())

