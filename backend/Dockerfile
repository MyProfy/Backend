FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
  build-essential libpq-dev && \
  rm -rf /var/lib/apt/lists/*

# requirements at project root
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy backend app code
COPY backend/ .

CMD ["gunicorn config.wsgi:application --bind 0.0.0.0:8000"]