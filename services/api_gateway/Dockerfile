FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY services/api_gateway/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY services/api_gateway/src ./src

EXPOSE 8080

CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]