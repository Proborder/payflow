# 🚀 Quick Start

## 1. ⚙️ Подготовка окружения

Сначала создайте файлы конфигурации из примеров

В payment-service:

```bash
cp payment-service/.env.example .env
cp payment-service/.env-test.example .env-test
```

В analytics-service:

```bash
cp analytics-service/.env.example .env
cp analytics-service/.env-test.example .env-test
```

---

## 2. 🐳 Запуск инфраструктуры (Docker)

Запустите базу данных, Redis и Kafka в фоновом режиме:

```bash
docker-compose up -d --build
```

---

## 3. 🧪 Подготовка базы данных для тестов

Тесты используют отдельную базу данных для изоляции, поэтому её нужно создать вручную (один раз):

```bash
docker exec -it payment_db psql -U postgres -c "CREATE DATABASE test;"
docker exec -it analytics_db psql -U postgres -c "CREATE DATABASE test;"
```

---

## 4. ▶️ Запуск приложения (локально)

Для удобной разработки и дебага запускайте сервис напрямую через Poetry:

```bash
cd payment-service

poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --port 8000
```

```bash
cd analytics-service

poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --port 8000
```

---

## 5. ✅ Запуск тестов

Выполните:

```bash
pytest
```

---

## 🛠 Полезные команды Docker

```bash
# Остановить все контейнеры
docker-compose down

# Просмотр логов приложения
docker logs -f

# Проверить статус контейнеров
docker ps
```
