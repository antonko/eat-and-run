FROM python:3.12-slim

# Установка UV
COPY --from=ghcr.io/astral-sh/uv:0.5.13 /uv /uvx /bin/

# Установка рабочей директории
WORKDIR /app

# Сначала копируем все файлы проекта
COPY . .

# Установка зависимостей без editable mode
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install --system .

# Создание и переключение на непривилегированного пользователя
RUN useradd -ms /bin/bash appuser && \
  chown -R appuser:appuser /app
USER appuser

# Запуск бота
CMD ["python", "run.py"]
