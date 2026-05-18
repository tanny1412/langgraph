FROM python:3.11-slim

WORKDIR /app

COPY session_13/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "session_10.main:app", "--host", "0.0.0.0", "--port", "8000"]
