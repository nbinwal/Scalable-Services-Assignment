FROM python:3.10-slim

WORKDIR /app

# Install dependencies needed for psycopg2 build (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
ENV PORT=5000

CMD ["python", "app.py"]