FROM python:3.12-slim

WORKDIR /service

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/service/src:/common/src

COPY services/news_service/requirements.txt /service/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /service/requirements.txt

COPY services/news_service/src /service/src
COPY common/src /common/src

CMD ["uvicorn", "news_service.main:app", "--host", "0.0.0.0", "--port", "8007"]