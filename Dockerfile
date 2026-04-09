FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "navis_web_env.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
