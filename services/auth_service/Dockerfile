FROM python:3.12-slim

WORKDIR /service

COPY services/auth_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/auth_service/src ./src
COPY services/auth_service/alembic.ini ./alembic.ini
COPY services/auth_service/alembic ./alembic
COPY common/src ./common/src

ENV PYTHONPATH=/service/src:/service/common/src

CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
