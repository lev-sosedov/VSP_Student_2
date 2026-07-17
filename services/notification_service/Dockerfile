FROM python:3.12-slim

WORKDIR /service

COPY services/notification_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/notification_service/src ./src
COPY common/src ./common/src

ENV PYTHONPATH=/service/src:/service/common/src
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "notification_service.main:app", "--host", "0.0.0.0", "--port", "8005"]