FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .

RUN pip install --no-cache-dir -r requirements-docker.txt pandas psycopg2-binary

COPY mlruns ./mlruns

EXPOSE 1234

CMD ["mlflow", "models", "serve", "-m", "/app/mlruns/1/models/m-b74ed6757286402db48a606ff9d2faaa/artifacts", "-p", "1234", "--host", "0.0.0.0", "--no-conda"]
