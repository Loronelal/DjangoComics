# Используем официальный образ Python
FROM python:3.9-slim

# Предотвращаем создание .pyc файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости, необходимые для сборки некоторых пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Собираем статические файлы (можно выполнить при старте)
RUN python manage.py collectstatic --noinput || true

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска сервера (для продакшена замените на gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]