# 🚀 Quick Start

## 1. ⚙️ Подготовка окружения

Сначала создайте файлы конфигурации в payment-serivce из примеров:

```bash
cp .env.example .env
cp .env-test.example .env-test
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
docker logs -f payment_app

# Проверить статус контейнеров
docker ps
```
