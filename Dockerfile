FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn clauseguard_mcp.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
