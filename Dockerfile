FROM python:3.9-slim

WORKDIR /app

# Установка необходимых системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .
COPY main.py .
COPY modules/ ./modules/

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Открытие порта для Flet
EXPOSE 8550

# Запуск приложения
CMD ["python", "main.py"] 