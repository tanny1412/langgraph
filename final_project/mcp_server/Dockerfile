FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY final_project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY final_project/ ./final_project/

EXPOSE 8080

CMD ["python3", "final_project/mcp_server/server.py"]
