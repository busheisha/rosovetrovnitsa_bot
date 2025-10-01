# Используем slim вместо alpine для лучшей совместимости с научными библиотеками
FROM python:3.12-slim

# Устанавливаем системные зависимости для matplotlib и других библиотек
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем зависимости (для кэширования слоя)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./bot /app/bot

# Создаем необходимые директории для файлов и изображений
RUN mkdir -p /app/bot/files/images

# Запускаем бота
CMD ["python3", "./bot/main.py"] 
