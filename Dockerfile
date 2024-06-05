# Вказуємо базовий образ
FROM python:3.12

# Встановлюємо робочий каталог
WORKDIR /app

# Встановлюємо Poetry
RUN pip install poetry

# Копіюємо pyproject.toml і poetry.lock для встановлення залежностей
COPY pyproject.toml poetry.lock /app/

# Встановлюємо залежності
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Копіюємо весь проект
COPY . /app/

# Вказуємо команду для запуску
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
