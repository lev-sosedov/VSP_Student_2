# OpenAPI baseline

Каталог `openapi/baseline` содержит зафиксированные схемы всех сервисов до
внедрения общей JWT-защиты. Они нужны для проверки, что security-изменения не
сломали пути, методы и модели frontend API.

Экспорт схем из исходного кода:

```powershell
python scripts/export_openapi.py
```

Проверка текущих схем против baseline:

```powershell
python scripts/export_openapi.py --check
```

Для экспорта должны быть установлены зависимости backend-сервисов. Скрипт не
запускает lifespan и не подключается к PostgreSQL или RabbitMQ.

При намеренном изменении API baseline обновляется отдельным коммитом после
проверки frontend и описания breaking change.
