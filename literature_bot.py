# literature_bot.py - современная версия для Python 3.13
import logging
import random
import json
import os
from typing import Dict, Any, List
import asyncio

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Токен бота
TELEGRAM_BOT_TOKEN = "8421692900:AAH8-5L37_6SeNYKQ_RwsUJbva-kV71F8QU"

# База данных книг (10 книг)
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
    },
    {
        "id": 6,
        "title": "Властелин колец: Братство кольца",
        "author": "Дж. Р. Р. Толкин",
        "genres": ["Фэнтези", "Эпическое"],
        "description": "Эпическая история о путешествии Фродо Бэггинса."
    },
    {
        "id": 7,
        "title": "Три товарища",
        "author": "Эрих Мария Ремарк",
        "genres": ["Классика", "Роман"],
        "description": "История о дружбе и любви в послевоенной Германии."
    },
    {
        "id": 8,
        "title": "Убить пересмешника",
        "author": "Харпер Ли",
        "genres": ["Классика", "Драма"],
        "description": "Пронзительная история о взрослении и неравенстве."
    },
    {
        "id": 9,
        "title": "Анна Каренина",
        "author": "Лев Толстой",
        "genres": ["Классика", "Роман"],
        "description": "Трагическая история любви замужней женщины."
    },
    {
        "id": 10,
        "title": "Маленький принц",
        "author": "Антуан де Сент-Экзюпери",
        "genres": ["Философия", "Притча"],
        "description": "Философская притча о маленьком мальчике с астероида."
    }
]

# Менеджер лайков
class LikeManager:
    def __init__(self, filename: str = "likes.json"):
        self.filename = filename
        self.likes_data = self._load_likes()
    
    def _load_likes(self) -> Dict[int, int]:
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки лайков: {e}")
            return {}
    
    def _save_likes(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.likes_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения лайков: {e}")
    
    def get_likes(self, book_id: int) -> int:
        return self.likes_data.get(str(book_id), 0)
    
    def add_like(self, book_id: int):
        book_id_str = str(book_id)
        current_likes = self.likes_data.get(book_id_str, 0)
        self.likes_data[book_id_str] = current_likes + 1
        self._save_likes()
        logger.info(f"Лайк книге {book_id}. Всего: {current_likes + 1}")
    
    def get_top_books(self, books_db: List[Dict], limit: int = 5) -> List[Dict]:
        books_with_likes = []
        for book in books_db:
            likes = self.get_likes(book["id"])
            books_with_likes.append({**book, "total_likes": likes})
        
        books_with_likes.sort(key=lambda x: x["total_likes"], reverse=True)
        return books_with_likes[:limit]

# Основной класс бота
class BookBot:
    def __init__(self):
        self.like_manager = LikeManager()
        self.user_states: Dict[int, Dict[str, Any]] = {}
        self.user_info: Dict[int, Dict[str, str]] = {}
        self.last_recommendations: Dict[int, Dict] = {}
    
    def get_available_genres(self) -> str:
        all_genres = set()
        for book in BOOKS_DATABASE:
            all_genres.update(book["genres"])
        return ", ".join(sorted(all_genres))
    
    def handle_start(self, user_id: int, user_name: str = "") -> str:
        self.user_states[user_id] = {"step": "start"}
        self.user_info[user_id] = {"name": user_name or "друг"}
        return (
            "📚 *Добро пожаловать в Литературный Гурман!*\n\n"
            f"В моей библиотеке *{len(BOOKS_DATABASE)}* замечательных книг!\n\n"
            "*Доступные команды:*\n"
            "/recommend - подобрать книгу\n"
            "/like - поставить лайк текущей книге\n"
            "/top - топ книг по лайкам\n"
            "/books - список всех книг\n"
            "/genres - доступные жанры\n"
            "/help - помощь\n\n"
            "Напиши */recommend* чтобы начать!"
        )
    
    def handle_recommend(self, user_id: int) -> str:
        self.user_states[user_id] = {"step": "asking_genre"}
        user_name = self.user_info.get(user_id, {}).get("name", "друг")
        return (
            f"Отлично, {user_name}! Давай подберем книгу.\n\n"
            "Напиши *один или несколько* любимых жанров через запятую.\n"
            "Например: *Фэнтези, Классика, Детектив*\n\n"
            f"*Доступные жанры:* {self.get_available_genres()}"
        )
    
    def handle_like(self, user_id: int) -> str:
        if user_id not in self.last_recommendations:
            return "❌ Сначала получи рекомендацию книги с помощью /recommend!"
        
        last_book = self.last_recommendations[user_id]
        book_id = last_book["id"]
        book_title = last_book["title"]
        
        self.like_manager.add_like(book_id)
        current_likes = self.like_manager.get_likes(book_id)
        
        return (
            f"❤️ *Отлично!* Ты поставил(а) лайк книге:\n"
            f"*{book_title}*\n\n"
            f"Теперь у этой книги *{current_likes}* лайков!\n\n"
            f"Посмотреть топ книг: /top"
        )
    
    def handle_top(self, user_id: int) -> str:
        top_books = self.like_manager.get_top_books(BOOKS_DATABASE, 5)
        
        if not top_books or all(book["total_likes"] == 0 for book in top_books):
            return "📊 Пока нет лайков. Будь первым, кто поставит лайк! ❤️"
        
        response = "🏆 *Топ книг по лайкам:*\n\n"
        
        for i, book in enumerate(top_books, 1):
            likes = book["total_likes"]
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📚"
            response += f"{emoji} *{book['title']}* - {book['author']}\n"
            response += f"   ❤️ {likes} лайков | 🏷️ {', '.join(book['genres'])}\n\n"
        
        return response + "_Поставь лайк понравившейся книге с помощью /like_"
    
    def handle_books(self, user_id: int) -> str:
        response = f"📖 *Все книги в библиотеке ({len(BOOKS_DATABASE)}):*\n\n"
        for i, book in enumerate(BOOKS_DATABASE, 1):
            likes = self.like_manager.get_likes(book["id"])
            likes_text = f" ❤️ {likes}" if likes > 0 else ""
            response += f"{i}. *{book['title']}* - {book['author']}{likes_text}\n"
            response += f"   🏷️ {', '.join(book['genres'])}\n\n"
        return response
    
    def handle_genres(self, user_id: int) -> str:
        return f"🏷️ *Доступные жанры:*\n\n{self.get_available_genres()}\n\nИспользуй команду /recommend для подбора книги!"
    
    def handle_help(self, user_id: int) -> str:
        return (
            "*📚 Литературный Гурман - Помощь*\n\n"
            "*Как пользоваться:*\n"
            "1. /recommend - подобрать книгу по жанру\n"
            "2. /like - поставить лайк понравившейся книге\n"
            "3. /top - посмотреть самые популярные книги\n\n"
            "*Все команды:*\n"
            "/start - начать диалог\n"
            "/recommend - подобрать книгу\n"
            "/like - поставить лайк\n"
            "/top - топ книг\n"
            "/books - список книг\n"
            "/genres - доступные жанры\n"
            "/help - эта справка\n\n"
            f"*В библиотеке:* {len(BOOKS_DATABASE)} книг"
        )
    
    def handle_message(self, user_id: int, user_input: str, user_name: str = "") -> str:
        user_input_lower = user_input.lower().strip()
        
        # Обработка команд
        commands = {
            "/start": self.handle_start,
            "/recommend": self.handle_recommend,
            "/like": self.handle_like,
            "/top": self.handle_top,
            "/books": self.handle_books,
            "/genres": self.handle_genres,
            "/help": self.handle_help
        }
        
        for cmd, handler in commands.items():
            if user_input_lower in [cmd, cmd[1:], self._get_russian_command(cmd)]:
                return handler(user_id)
        
        # Сохраняем имя пользователя
        if user_name and user_id not in self.user_info:
            self.user_info[user_id] = {"name": user_name}
        
        # Обработка диалога
        user_state = self.user_states.get(user_id, {"step": "start"})
        
        if user_state["step"] == "asking_genre":
            return self._process_genre_selection(user_id, user_input, user_state)
        
        return self._get_unknown_command_response()
    
    def _get_russian_command(self, command: str) -> str:
        russian_commands = {
            "/start": "старт",
            "/recommend": "рекомендовать",
            "/like": "лайк", 
            "/top": "топ",
            "/books": "книги",
            "/genres": "жанры",
            "/help": "помощь"
        }
        return russian_commands.get(command, command[1:])
    
    def _process_genre_selection(self, user_id: int, user_input: str, user_state: Dict[str, Any]) -> str:
        genres = [genre.strip() for genre in user_input.split(",")]
        user_state["preferred_genres"] = genres
        user_state["step"] = "done"
        
        # Подбор книги
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
        
        selected_book = random.choice(filtered_books)
        self.last_recommendations[user_id] = selected_book
        
        likes_count = self.like_manager.get_likes(selected_book["id"])
        likes_info = f"❤️ {likes_count} лайков" if likes_count > 0 else "Будь первым, кто поставит лайк! ❤️"
        
        user_name = self.user_info.get(user_id, {}).get("name", "друг")
        
        return (
            f"{message}"
            f"📖 *{selected_book['title']}*\n"
            f"✍️ *Автор:* {selected_book['author']}\n"
            f"🏷️ *Жанры:* {', '.join(selected_book['genres'])}\n"
            f"📝 *Описание:* {selected_book['description']}\n"
            f"⭐ *Популярность:* {likes_info}\n\n"
            f"Приятного чтения, {user_name}! 📚\n\n"
            "*Что дальше?*\n"
            "• /like - поставить лайк этой книге\n"
            "• /top - посмотреть топ книг\n" 
            "• /recommend - новая рекомендация"
        )
    
    def _get_unknown_command_response(self) -> str:
        return (
            "Я не совсем понимаю. 😕\n\n"
            "*Используй команды:*\n"
            "/recommend - подобрать книгу\n"
            "/like - поставить лайк\n" 
            "/top - топ книг\n"
            "/books - список книг\n"
            "/help - помощь"
        )

# Инициализация бота
book_bot = BookBot()

# Telegram обработчики (асинхронные для версии 21.7)
async def start_command(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or ""
    response = book_bot.handle_start(user_id, user_name)
    await update.message.reply_text(response, parse_mode='Markdown')

async def recommend_command(update, context):
    user_id = update.effective_user.id
    response = book_bot.handle_recommend(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def like_command(update, context):
    user_id = update.effective_user.id
    response = book_bot.handle_like(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def top_command(update, context):
    user_id = update.effective_user.id
    response = book_bot.handle_top(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def books_command(update, context):
    user_id = update.effective_user.id
    response = book_bot.handle_books(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def genres_command(update, context):
    user_id = update.effective_user.id
    response = book_bot.handle_genres(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def help_command(update, context):
    user_id = update.effective_user.id
    response = book_bot.handle_help(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_user_message(update, context):
    user_id = update.effective_user.id
    user_input = update.message.text
    user_name = update.effective_user.first_name or ""
    response = book_bot.handle_message(user_id, user_input, user_name)
    await update.message.reply_text(response, parse_mode='Markdown')

async def main():
    print("🚀 Запуск Литературного Гурмана на Render.com...")
    print(f"📚 В библиотеке: {len(BOOKS_DATABASE)} книг")
    print("✅ Бот инициализирован и готов к работе!")
    
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики
        handlers = [
            CommandHandler("start", start_command),
            CommandHandler("recommend", recommend_command),
            CommandHandler("like", like_command),
            CommandHandler("top", top_command),
            CommandHandler("books", books_command),
            CommandHandler("genres", genres_command),
            CommandHandler("help", help_command),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message)
        ]
        
        for handler in handlers:
            application.add_handler(handler)
        
        # Запускаем бота
        print("🔍 Начинаем прослушивание сообщений...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    # Проверяем зависимости
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        print("✅ Все зависимости загружены успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что установлены все зависимости:")
        print("pip install python-telegram-bot==21.7")
        exit(1)
    
    # Запускаем бота
    asyncio.run(main())
