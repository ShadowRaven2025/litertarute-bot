import logging
import random
import json
import os
from typing import Dict, Any, List
import requests

# Настройка логирования для отслеживания работы бота
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ========== КОНФИГУРАЦИЯ (Здесь пользователь подставит свои ключи) ==========
# Эти переменные должны быть заполнены перед запуском
TELEGRAM_BOT_TOKEN = "8421692900:AAH8-5L37_6SeNYKQ_RwsUJbva-kV71F8QU"
YANDEX_GPT_API_KEY = "YANDEX_GPT_API_KEY_HERE"  # Ключ от Yandex Cloud
YANDEX_CATALOG_ID = "b1ghcfp4djt05fgks12j"    # ID каталога в Yandex Cloud

# ========== БАЗА ДАННЫХ КНИГ (Расширенная библиотека) ==========
BOOKS_DATABASE = [
    {
        "id": 1,
        "title": "Хоббит, или Туда и обратно",
        "author": "Дж. Р. Р. Толкин",
        "genres": ["Фэнтези", "Приключения"],
        "description": "Классическая история о путешествии Бильбо Бэггинса.",
        "mood": ["Приподнятое", "Эпическое", "Доброе"],
        "likes": 0
    },
    {
        "id": 2,
        "title": "Убить пересмешника",
        "author": "Харпер Ли",
        "genres": ["Классика", "Роман", "Драма"],
        "description": "Пронзительная история о взрослении и неравенстве в американском южном штате.",
        "mood": ["Задумчивое", "Эмоциональное", "Сильное"],
        "likes": 0
    },
    {
        "id": 3,
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "genres": ["Классика", "Мистика", "Сатира"],
        "description": "Мистический роман о визите дьявола в Москву 1930-х годов.",
        "mood": ["Мистическое", "Загадочное", "Философское"],
        "likes": 0
    },
    {
        "id": 4,
        "title": "Игра Эндера",
        "author": "Орсон Скотт Кард",
        "genres": ["Научная фантастика"],
        "description": "История о юном гении, которого готовят к защите Земли от инопланетной угрозы.",
        "mood": ["Напряженное", "Интеллектуальное", "Эпическое"],
        "likes": 0
    },
    {
        "id": 5,
        "title": "Три товарища",
        "author": "Эрих Мария Ремарк",
        "genres": ["Классика", "Роман"],
        "description": "История о дружбе и любви на фоне трудностей послевоенной Германии.",
        "mood": ["Ностальгическое", "Лирическое", "Грустное"],
        "likes": 0
    },
    {
        "id": 6,
        "title": "1984",
        "author": "Джордж Оруэлл",
        "genres": ["Антиутопия", "Научная фантастика", "Классика"],
        "description": "Роман-антиутопия о тоталитарном обществе под постоянным контролем Большого Брата.",
        "mood": ["Тревожное", "Философское", "Мрачное"],
        "likes": 0
    },
    {
        "id": 7,
        "title": "Гарри Поттер и философский камень",
        "author": "Джоан Роулинг",
        "genres": ["Фэнтези", "Приключения", "Детская литература"],
        "description": "Первая книга о юном волшебнике Гарри Поттере и его обучении в Хогвартсе.",
        "mood": ["Волшебное", "Приключенческое", "Захватывающее"],
        "likes": 0
    },
    {
        "id": 8,
        "title": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "genres": ["Классика", "Психологический роман", "Философия"],
        "description": "История бывшего студента Родиона Раскольникова, совершившего убийство.",
        "mood": ["Психологическое", "Драматическое", "Философское"],
        "likes": 0
    },
    {
        "id": 9,
        "title": "Маленький принц",
        "author": "Антуан де Сент-Экзюпери",
        "genres": ["Философия", "Притча", "Детская литература"],
        "description": "Философская притча о маленьком мальчике с астероида Б-612.",
        "mood": ["Поэтическое", "Философское", "Трогательное"],
        "likes": 0
    },
    {
        "id": 10,
        "title": "Властелин колец: Братство кольца",
        "author": "Дж. Р. Р. Толкин",
        "genres": ["Фэнтези", "Приключения", "Эпическое"],
        "description": "Первая часть эпопеи о Средиземье и путешествии хоббита Фродо Бэггинса.",
        "mood": ["Эпическое", "Приключенческое", "Героическое"],
        "likes": 0
    },
    {
        "id": 11,
        "title": "Шерлок Холмс: Этюд в багровых тонах",
        "author": "Артур Конан Дойл",
        "genres": ["Детектив", "Классика"],
        "description": "Первое дело Шерлока Холмса, в котором он знакомится с доктором Ватсоном.",
        "mood": ["Загадочное", "Интеллектуальное", "Напряженное"],
        "likes": 0
    },
    {
        "id": 12,
        "title": "Анна Каренина",
        "author": "Лев Толстой",
        "genres": ["Классика", "Роман", "Драма"],
        "description": "Трагическая история любви замужней женщины к блестящему офицеру.",
        "mood": ["Драматическое", "Эмоциональное", "Трагическое"],
        "likes": 0
    },
    {
        "id": 13,
        "title": "Дюна",
        "author": "Фрэнк Герберт",
        "genres": ["Научная фантастика", "Эпическое"],
        "description": "Эпическая сага о пустынной планете Арракис и её спайсе меланже.",
        "mood": ["Эпическое", "Философское", "Приключенческое"],
        "likes": 0
    },
    {
        "id": 14,
        "title": "Портрет Дориана Грея",
        "author": "Оскар Уайльд",
        "genres": ["Классика", "Философия", "Готика"],
        "description": "История о молодом человеке, чей портрет стареет вместо него.",
        "mood": ["Мистическое", "Философское", "Драматическое"],
        "likes": 0
    },
    {
        "id": 15,
        "title": "Старик и море",
        "author": "Эрнест Хемингуэй",
        "description": "История о старом рыбаке Сантьяго и его борьбе с гигантской рыбой.",
        "genres": ["Классика", "Драма"],
        "mood": ["Философское", "Героическое", "Задумчивое"],
        "likes": 0
    },
    {
        "id": 16,
        "title": "Гордость и предубеждение",
        "author": "Джейн Остин",
        "genres": ["Классика", "Роман", "Комедия"],
        "description": "История любви Элизабет Беннет и мистера Дарси в Англии XIX века.",
        "mood": ["Романтическое", "Остроумное", "Легкое"],
        "likes": 0
    },
    {
        "id": 17,
        "title": "Метро 2033",
        "author": "Дмитрий Глуховский",
        "genres": ["Постапокалипсис", "Научная фантастика", "Ужасы"],
        "description": "Постапокалиптический роман о жизни в московском метро после ядерной войны.",
        "mood": ["Мрачное", "Напряженное", "Мистическое"],
        "likes": 0
    },
    {
        "id": 18,
        "title": "Алиса в Стране чудес",
        "author": "Льюис Кэрролл",
        "genres": ["Фэнтези", "Детская литература", "Абсурд"],
        "description": "Сказка о девочке Алисе, попавшей в подземную страну через кроличью нору.",
        "mood": ["Фантастическое", "Остроумное", "Загадочное"],
        "likes": 0
    },
    {
        "id": 19,
        "title": "Тёмные начала",
        "author": "Филип Пулман",
        "genres": ["Фэнтези", "Приключения"],
        "description": "История Лиры Белаквы в параллельном мире, где у людей есть деймоны.",
        "mood": ["Приключенческое", "Философское", "Захватывающее"],
        "likes": 0
    },
    {
        "id": 20,
        "title": "Код да Винчи",
        "author": "Дэн Браун",
        "genres": ["Детектив", "Триллер"],
        "description": "Интеллектуальный триллер о тайнах Леонардо да Винчи и истории христианства.",
        "mood": ["Захватывающее", "Интеллектуальное", "Напряженное"],
        "likes": 0
    },
    {
        "id": 21,
        "title": "Над пропастью во ржи",
        "author": "Джером Д. Сэлинджер",
        "genres": ["Классика", "Роман"],
        "description": "История подростка Холдена Колфилда и его бунта против взрослого мира.",
        "mood": ["Ностальгическое", "Задумчивое", "Бунтарское"],
        "likes": 0
    },
    {
        "id": 22,
        "title": "Автостопом по галактике",
        "author": "Дуглас Адамс",
        "genres": ["Научная фантастика", "Комедия"],
        "description": "Юмористическая история о землянине Артуре Денте и его межгалактических приключениях.",
        "mood": ["Юмористическое", "Абсурдное", "Легкое"],
        "likes": 0
    },
    {
        "id": 23,
        "title": "Война и мир",
        "author": "Лев Толстой",
        "genres": ["Классика", "Исторический роман", "Эпическое"],
        "description": "Эпопея о жизни русского общества во время наполеоновских войн.",
        "mood": ["Эпическое", "Историческое", "Философское"],
        "likes": 0
    },
    {
        "id": 24,
        "title": "Фауст",
        "author": "Иоганн Вольфганг Гёте",
        "genres": ["Классика", "Философия", "Трагедия"],
        "description": "Философская драма о докторе Фаусте, заключившем сделку с дьяволом.",
        "mood": ["Философское", "Трагическое", "Глубокое"],
        "likes": 0
    },
    {
        "id": 25,
        "title": "Сто лет одиночества",
        "author": "Габриэль Гарсиа Маркес",
        "genres": ["Магический реализм", "Классика"],
        "description": "Сага о семье Буэндиа в вымышленном городе Макондо.",
        "mood": ["Магическое", "Поэтическое", "Философское"],
        "likes": 0
    }
]

# ========== ФАЙЛ ДЛЯ СОХРАНЕНИЯ ЛАЙКОВ ==========
LIKES_FILE = "book_likes.json"

class LikeManager:
    """Класс для управления лайками книг."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.likes_data = self._load_likes()
    
    def _load_likes(self) -> Dict[int, int]:
        """Загружает данные о лайках из файла."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки лайков: {e}")
            return {}
    
    def _save_likes(self):
        """Сохраняет данные о лайках в файл."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.likes_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения лайков: {e}")
    
    def get_likes(self, book_id: int) -> int:
        """Возвращает количество лайков для книги."""
        return self.likes_data.get(str(book_id), 0)
    
    def add_like(self, book_id: int):
        """Добавляет лайк книге."""
        book_id_str = str(book_id)
        current_likes = self.likes_data.get(book_id_str, 0)
        self.likes_data[book_id_str] = current_likes + 1
        self._save_likes()
        logger.info(f"Добавлен лайк книге ID {book_id}. Теперь лайков: {current_likes + 1}")
    
    def get_top_books(self, books_db: List[Dict], limit: int = 5) -> List[Dict]:
        """Возвращает топ книг по лайкам."""
        books_with_likes = []
        for book in books_db:
            likes = self.get_likes(book["id"])
            books_with_likes.append({**book, "total_likes": likes})
        
        # Сортируем по убыванию лайков
        books_with_likes.sort(key=lambda x: x["total_likes"], reverse=True)
        return books_with_likes[:limit]

# ========== КЛАСС ДЛЯ РАБОТЫ С YANDEX GPT ==========
class YandexGPT:
    """
    Класс для генерации текстовых ответов с помощью YandexGPT.
    Обеспечивает безопасность: API-ключ не передается в коде, а берется из переменной окружения.
    """

    def __init__(self, api_key: str, catalog_id: str):
        self.api_key = api_key
        self.catalog_id = catalog_id
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.catalog_id
        }

    def generate_annotation(self, book_title: str, book_author: str, original_description: str) -> str:
        """
        Генерирует креативную и короткую аннотацию для книги, чтобы заинтриговать пользователя.

        Args:
            book_title (str): Название книги.
            book_author (str): Автор книги.
            original_description (str): Оригинальное описание из базы.

        Returns:
            str: Сгенерированная аннотация или заглушка в случае ошибки.
        """
        # Промпт тщательно составлен для получения нужного формата и стиля.
        prompt = {
            "modelUri": f"gpt://{self.catalog_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,  # Достаточно креативности, но не слишком
                "maxTokens": 150    # Короткий ответ
            },
            "messages": [
                {
                    "role": "system",
                    "text": (
                        "Ты — умный и увлекательный литературный критик. "
                        "Сгенерируй очень краткую (2-3 предложения) аннотацию для книги, "
                        "которая звучала бы как описание на обложке. "
                        "Цель — заинтересовать и захватить потенциального читателя. "
                        "Не упоминай название книги и автора в теле аннотации, они и так будут указаны отдельно. "
                        "Используй яркие образы и интригующие формулировки. "
                        "Отвечай только текстом аннотации, без лишних слов."
                    )
                },
                {
                    "role": "user",
                    "text": (
                        f"Название: {book_title}. Автор: {book_author}. "
                        f"Исходное описание: {original_description}. "
                        "Сгенерируй аннотацию."
                    )
                }
            ]
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=prompt)
            response.raise_for_status()  # Вызовет исключение для кодов 4xx/5xx
            result = response.json()
            generated_text = result['result']['alternatives'][0]['message']['text']
            # Очистка ответа от возможных кавычек или лишних точек
            cleaned_text = generated_text.strip().strip('"').strip('"').strip('"')
            return cleaned_text

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к YandexGPT: {e}")
        except (KeyError, IndexError) as e:
            logger.error(f"Ошибка разбора ответа от YandexGPT: {e}")

        # Возвращаем заглушку в случае любой ошибки
        return original_description

# ========== ОСНОВНАЯ ЛОГИКА БОТА ==========
class BookBot:
    """Класс, обрабатывающий логику чат-бота."""

    def __init__(self, gpt_client: YandexGPT):
        self.gpt = gpt_client
        self.like_manager = LikeManager(LIKES_FILE)
        # Словарь для хранения состояния пользователя (шаг анкеты, жанры и т.д.)
        self.user_states: Dict[int, Dict[str, Any]] = {}
        # Словарь для хранения информации о пользователях (имя)
        self.user_info: Dict[int, Dict[str, str]] = {}
        # Словарь для хранения последней рекомендованной книги пользователю
        self.last_recommendations: Dict[int, Dict] = {}

    def handle_start(self, user_id: int, user_name: str = "") -> str:
        """Обработка команды /start."""
        self.user_states[user_id] = {"step": "start"}
        # Сохраняем информацию о пользователе
        self.user_info[user_id] = {"name": user_name or "друг"}
        return (
            "📚 Добро пожаловать в *Литературный Гурман*!\n\n"
            "Я помогу тебе найти следующую книгу для чтения. "
            f"В моей библиотеке *{len(BOOKS_DATABASE)}* замечательных книг!\n\n"
            "*Доступные команды:*\n"
            "/recommend - подобрать книгу\n"
            "/like - поставить лайк текущей книге\n"
            "/top - топ книг по лайкам\n"
            "/help - помощь\n\n"
            "Напиши *'/recommend'*, чтобы начать!"
        )

    def handle_recommend(self, user_id: int) -> str:
        """Начинает опрос для рекомендации."""
        self.user_states[user_id] = {"step": "asking_genre"}
        user_name = self.user_info.get(user_id, {}).get("name", "друг")
        return (
            f"Отлично, {user_name}! Давай подберем тебе книгу.\n"
            "Для начала назови *один или несколько* любимых жанров через запятую.\n"
            "Например: *Фэнтези, Научная фантастика, Детектив*\n\n"
            f"*Доступные жанры:* {self._get_available_genres()}"
        )

    def _get_available_genres(self) -> str:
        """Возвращает строку с доступными жанрами."""
        all_genres = set()
        for book in BOOKS_DATABASE:
            all_genres.update(book["genres"])
        return ", ".join(sorted(all_genres))

    def handle_like(self, user_id: int) -> str:
        """Обработка команды /like - ставит лайк последней рекомендованной книге."""
        if user_id not in self.last_recommendations:
            return "Сначала получи рекомендацию книги с помощью команды /recommend! 📖"
        
        last_book = self.last_recommendations[user_id]
        book_id = last_book["id"]
        book_title = last_book["title"]
        
        self.like_manager.add_like(book_id)
        current_likes = self.like_manager.get_likes(book_id)
        
        return (
            f"❤️ *Отлично!* Ты поставил(а) лайк книге:\n"
            f"*{book_title}*\n\n"
            f"Теперь у этой книги *{current_likes}* лайков!\n\n"
            f"Хочешь посмотреть топ книг? Напиши */top*"
        )

    def handle_top(self, user_id: int) -> str:
        """Обработка команды /top - показывает топ книг по лайкам."""
        top_books = self.like_manager.get_top_books(BOOKS_DATABASE, limit=5)
        
        if not top_books:
            return "Пока нет лайков. Будь первым, кто поставит лайк! ❤️"
        
        response = "🏆 *Топ книг по лайкам:*\n\n"
        
        for i, book in enumerate(top_books, 1):
            likes = book["total_likes"]
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📚"
            response += f"{emoji} *{book['title']}* - {book['author']}\n"
            response += f"   ❤️ {likes} лайков\n"
            response += f"   🏷️ {', '.join(book['genres'])}\n\n"
        
        response += "_Поставь лайк понравившейся книге с помощью /like после рекомендации!_"
        return response

    def handle_message(self, user_id: int, user_input: str, user_name: str = "") -> str:
        """
        Основной обработчик сообщений пользователя.
        Ведет диалог по шагам на основе состояния (state) пользователя.
        """
        # Приводим входные данные к нижнему регистру для более простого сравнения
        user_input_lower = user_input.lower()

        # Проверка на простые команды вне потока рекомендаций
        if user_input_lower in ("/start", "start", "начать"):
            return self.handle_start(user_id, user_name)
        if user_input_lower in ("/recommend", "recommend", "подобрать"):
            return self.handle_recommend(user_id)
        if user_input_lower in ("/like", "like", "лайк"):
            return self.handle_like(user_id)
        if user_input_lower in ("/top", "top", "топ"):
            return self.handle_top(user_id)
        if user_input_lower in ("/help", "help", "помощь"):
            return (
                "*Доступные команды:*\n\n"
                "/start - начать работу\n"
                "/recommend - подобрать книгу\n"
                "/like - поставить лайк текущей книге\n"
                "/top - топ книг по лайкам\n"
                "/help - помощь\n\n"
                "*Как это работает:*\n"
                "1. Используй /recommend для подбора книги\n"
                "2. Если книга понравилась - поставь лайк /like\n"
                "3. Смотри топ книг в /top\n\n"
                f"*В библиотеке:* {len(BOOKS_DATABASE)} книг"
            )

        # Сохраняем имя пользователя, если оно передано
        if user_name and user_id not in self.user_info:
            self.user_info[user_id] = {"name": user_name}

        # Получаем текущее состояние пользователя. Если его нет, инициализируем.
        user_state = self.user_states.get(user_id, {"step": "start"})

        # Логика обработки в зависимости от шага, на котором находится пользователь
        if user_state["step"] == "asking_genre":
            # Сохраняем введенные жанры и переходим к следующему шагу
            user_state["preferred_genres"] = [genre.strip() for genre in user_input.split(",")]
            user_state["step"] = "asking_mood"
            user_name = self.user_info.get(user_id, {}).get("name", "друг")
            return (
                f"Прекрасный выбор, {user_name}! А какое у тебя сейчас *настроение*?\n"
                "Хочется чего-то *захватывающего*, *расслабляющего*, *грустного*, *вдохновляющего*?"
            )

        elif user_state["step"] == "asking_mood":
            # Сохраняем настроение и приступаем к подбору книги
            user_state["preferred_mood"] = user_input
            user_state["step"] = "recommending"

            # Вызываем функцию подбора книги
            recommendation = self._generate_recommendation(user_state, user_id)
            return recommendation

        # Если состояние неизвестно или пользователь просто что-то пишет
        return (
            "Я не совсем понимаю. 😕\n"
            "Напиши *'/recommend'*, чтобы подобрать книгу, или *'/help'*, если нужна помощь."
        )

    def _generate_recommendation(self, user_state: Dict[str, Any], user_id: int) -> str:
        """
        Основная логика подбора рекомендации на основе предпочтений пользователя.
        Использует LLM для генерации аннотации.
        """
        preferred_genres = user_state.get("preferred_genres", [])
        preferred_mood = user_state.get("preferred_mood", "").lower()
        
        # Получаем имя пользователя
        user_name = self.user_info.get(user_id, {}).get("name", "друг")

        # 1. Фильтрация книг по жанру
        genre_filtered_books = []
        for book in BOOKS_DATABASE:
            # Проверяем, есть ли пересечение между жанрами книги и предпочтениями пользователя
            book_genres_lower = [g.lower() for g in book["genres"]]
            user_genres_lower = [g.lower() for g in preferred_genres]
            if any(genre in book_genres_lower for genre in user_genres_lower):
                genre_filtered_books.append(book)

        # Если ни одна книга не подошла по жанру, используем всю базу
        if not genre_filtered_books:
            genre_filtered_books = BOOKS_DATABASE
            message_line = f"{user_name}, к сожалению, у меня мало книг в этом жанре. Но вот случайная рекомендация из моей библиотеки!\n\n"
        else:
            message_line = f"{user_name}, вот что я подобрал для тебя! 🔍\n\n"

        # 2. Попытка фильтрации по настроению (если книги остались после фильтра по жанру)
        mood_filtered_books = []
        if preferred_mood:
            for book in genre_filtered_books:
                book_moods_lower = [m.lower() for m in book.get("mood", [])]
                if any(mood in book_moods_lower for mood in preferred_mood.split()):
                    mood_filtered_books.append(book)

        # Выбираем финальный пул для рекомендации: либо отфильтрованный по настроению, либо по жанру
        final_books_pool = mood_filtered_books if mood_filtered_books else genre_filtered_books

        # 3. Случайным образом выбираем одну книгу из финального пула
        selected_book = random.choice(final_books_pool)

        # Сохраняем последнюю рекомендацию для пользователя (для функции лайков)
        self.last_recommendations[user_id] = selected_book

        # 4. Получаем количество лайков для этой книги
        likes_count = self.like_manager.get_likes(selected_book["id"])

        # 5. Генерируем аннотацию с помощью LLM
        generated_annotation = self.gpt.generate_annotation(
            selected_book["title"],
            selected_book["author"],
            selected_book["description"]
        )

        # 6. Формируем красивый ответ для пользователя
        likes_info = f"❤️ {likes_count} лайков" if likes_count > 0 else "Будь первым, кто поставит лайк! ❤️"
        
        response = (
            f"{message_line}"
            f"*{selected_book['title']}* - *{selected_book['author']}*\n\n"
            f"📖 *Аннотация:*\n{generated_annotation}\n\n"
            f"📚 *Жанр(ы):* {', '.join(selected_book['genres'])}\n"
            f"⭐ *Популярность:* {likes_info}\n\n"
            f"Приятного чтения, {user_name}! Надеюсь, тебе понравится. 😊\n\n"
            "*Что дальше?*\n"
            "• Напиши */like* чтобы поставить лайк этой книге\n"
            "• Напиши */top* чтобы посмотреть топ книг\n"
            "• Напиши */recommend* для новой рекомендации"
        )
        return response

# ========== ИНТЕГРАЦИЯ С TELEGRAM ==========

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Глобальные переменные для экземпляров бота и GPT
book_bot = None
gpt_client = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start в Telegram."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or ""
    response = book_bot.handle_start(user_id, user_name)
    await update.message.reply_text(response, parse_mode='Markdown')

async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /recommend в Telegram."""
    user_id = update.effective_user.id
    response = book_bot.handle_recommend(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /like в Telegram."""
    user_id = update.effective_user.id
    response = book_bot.handle_like(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /top в Telegram."""
    user_id = update.effective_user.id
    response = book_bot.handle_top(user_id)
    await update.message.reply_text(response, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /help в Telegram."""
    user_id = update.effective_user.id
    response = book_bot.handle_message(user_id, "/help")
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все текстовые сообщения пользователя в Telegram."""
    user_id = update.effective_user.id
    user_input = update.message.text
    user_name = update.effective_user.first_name or ""
    response = book_bot.handle_message(user_id, user_input, user_name)
    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    """Основная функция для запуска бота."""
    # Загрузка конфигурации (на практике ключи лучше хранить в переменных окружения)
    global book_bot, gpt_client

    # Инициализация клиента GPT и бота
    gpt_client = YandexGPT(api_key=YANDEX_GPT_API_KEY, catalog_id=YANDEX_CATALOG_ID)
    book_bot = BookBot(gpt_client)

    # Создаем приложение и передаем ему токен бота
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("recommend", recommend_command))
    application.add_handler(CommandHandler("like", like_command))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    # Запускаем бота
    logger.info("Бот 'Литературный Гурман' запущен!")
    application.run_polling()

# Точка входа. Код выполняется только при прямом запуске скрипта.
if __name__ == "__main__":
    main()