# Конфигурация окружений

## Локальная разработка

1. Создайте локальные файлы конфигурации:

   ```powershell
   python scripts/bootstrap_env.py
   ```

2. Замените все значения `CHANGE_ME` в корневом `.env`.
3. Запустите проект обычной командой:

   ```powershell
   docker compose up -d --build
   ```

`docker-compose.override.yml` подключается автоматически. Все порты
привязаны к `127.0.0.1`, поэтому Swagger и инфраструктура доступны только
на локальном компьютере.

> **Важно:** при переходе на новую конфигурацию нельзя менять Docker Compose project name.
> Иначе Docker подключит новые пустые volumes вместо существующих `postgres_data` и
> `rabbitmq_data`.

Каждый микросервис использует отдельную логическую базу PostgreSQL. Имена баз задаются
переменными `AUTH_DB_NAME`, `USER_DB_NAME`, `ACADEMIC_DB_NAME`, `SCHEDULE_DB_NAME`,
`CONTENT_DB_NAME`, `COMMUNICATION_DB_NAME`, `NOTIFICATION_DB_NAME` и `NEWS_DB_NAME`.
Не заменяйте их одной общей `POSTGRES_DB`: это направит сервисы в другую логическую
базу внутри того же volume и сделает существующие данные недоступными приложению.

## Production

Production запускается без development override:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d --build
```

В production наружу публикуется только API Gateway на localhost. Nginx или
Caddy должен принимать HTTPS и проксировать `/api` и WebSocket-запросы на
`127.0.0.1:8080`.

PostgreSQL, RabbitMQ, Redis и порты `8000-8007` не должны публиковаться в
интернет.

## Правила секретов

- Файлы `.env` никогда не коммитятся.
- В `.env.example` находятся только безопасные примеры.
- Production-секреты хранятся в защищённом хранилище сервера или CI/CD.
- Значения с префиксом `VITE_` нельзя использовать для backend-секретов.
- После попадания секрета в Git его необходимо заменить, даже если файл
  позднее удалён.
- Для проверки репозитория выполните:

  ```powershell
  python scripts/check_configuration.py
  ```

## Обязательные production-значения

- `POSTGRES_PASSWORD`
- `AUTH_DB_NAME`, `USER_DB_NAME`, `ACADEMIC_DB_NAME`, `SCHEDULE_DB_NAME`
- `CONTENT_DB_NAME`, `COMMUNICATION_DB_NAME`, `NOTIFICATION_DB_NAME`, `NEWS_DB_NAME`
- `RABBITMQ_PASSWORD`
- `REDIS_PASSWORD`
- `JWT_PRIVATE_KEY_HOST_PATH` (auth-service only)
- `JWT_PUBLIC_KEY_HOST_PATH` (verifying HTTP services)
- `JWT_ALGORITHM=RS256`, `JWT_ISSUER`, `JWT_AUDIENCE`
- `CORS_ORIGINS=https://vsp-student.ru`
- SMTP-параметры, если включена отправка email

Приватный RSA-ключ никогда не попадает в Git или образы проверяющих сервисов.
Сгенерируйте локальную пару вне репозитория скриптом
`scripts/generate_jwt_keys.ps1` и задайте пути через `.env`. После перехода на
RS256 HS256 больше не поддерживается.
