#  Rozovetrovnitsa Bot

Спасибо прекрасным ЛЛМ за то, что написали такое чудесное ридми, сама бы я не сподобилась.

Telegram-бот для визуализации метеорологических данных: розы ветров, температура, влажность и осадки. Он нужен для кинологов, которые ищут пропавших людей, чтобы анализировать распространение запаха.

##  Возможности

- **Роза ветров** - совмещенная визуализация обычной и "умной" розы ветров (с учетом временного веса, так как старые ветры менее значимы в формировании облаков запаха)
- **Температура и влажность** - scatter plot с цветовой кодировкой
- **Осадки** - график осадков с высотой снежного покрова

##  Быстрый старт с Docker

### 1. Клонируй репозиторий
```bash
git clone <repository_url>
cd bot
```

### 2. Создай файл `.env`
```bash
# Скопируй .env.example и добавь свой токен
TG_TOKEN=your_telegram_bot_token_here
```

Токен можно получить у [@BotFather](https://t.me/BotFather) в Telegram.

### 3. Запусти через Docker Compose

**С помощью Makefile (рекомендуется):**
```bash
make up       # Запустить бота
make logs     # Просмотр логов
make restart  # Перезапустить
make down     # Остановить
make help     # Все команды
```

**Или напрямую через docker-compose:**
```bash
# Собрать и запустить
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановить
docker-compose down
```

##  Запуск без Docker

### 1. Установи зависимости
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Создай `.env` файл с токеном

### 3. Запусти бота
```bash
python bot/main.py
```

## Использование

1. Отправь боту `.xls.gz` файл с метеоданными
2. Получи визуализации:
   - Совмещенная роза ветров
   - График температуры и влажности
   - График осадков

##  Технологии

- Python 3.12
- python-telegram-bot
- Matplotlib (визуализация)
- Pandas (обработка данных)
- NumPy

##  Структура проекта

```
bot/
├── bot/
│   ├── main.py              # Основной файл бота
│   ├── rozovetrovnitsa.py   # Логика визуализаций
│   ├── messages.py          # Сообщения бота
│   └── files/               # Временные файлы (создается автоматически)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```
