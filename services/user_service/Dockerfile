FROM python:3.12-slim

WORKDIR /service

COPY services/user_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/user_service/src ./src
COPY common/src ./common/src

ENV PYTHONPATH=/service/src:/service/common/src

CMD ["uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--port", "8001"]