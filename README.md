#  Rozovetrovnitsa Bot

Спасибо прекрасным ЛЛМ за то, что написали такое чудесное ридми, сама бы я не сподобилась.

Telegram-бот для визуализации метеорологических данных: розы ветров, температура, влажность и осадки. Он нужен для кинологов, которые ищут пропавших людей, чтобы анализировать распространение запаха.

##  Возможности

- **Роза ветров** — совмещённая визуализация обычной и «умной» розы (с учётом скорости ветра и временного веса: старые ветры менее значимы для облака запаха)
- **Температура и влажность** — scatter plot с цветовой кодировкой
- **Осадки** — график осадков с высотой снежного покрова
- **ADD и TBS** — оценка накопленных градусо-суток и грубая стадия посмертных изменений (шкала Медьёзи по TBS и «интуитивная» шкала в вердикте; не замена экспертизе)

##  Быстрый старт с Docker

### 1. Клонируй репозиторий
```bash
git clone https://github.com/busheisha/rosovetrovnitsa_bot.git
cd rosovetrovnitsa_bot
```

### 2. Создай файл `bot/.env`
```bash
TG_TOKEN=your_telegram_bot_token_here
```

Токен — у [@BotFather](https://t.me/BotFather). Свой user id можно узнать у [@userinfobot](https://t.me/userinfobot).

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
   - Предположение о стадии декомпозиции (без картинки)

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
