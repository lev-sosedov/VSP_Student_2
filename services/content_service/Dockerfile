FROM python:3.12-slim

WORKDIR /service

COPY services/content_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/content_service/src ./src
COPY common/src ./common/src

ENV PYTHONPATH=/service/src:/service/common/src
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "content_service.main:app", "--host", "0.0.0.0", "--port", "8004"]

