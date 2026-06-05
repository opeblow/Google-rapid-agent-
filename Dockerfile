FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY agent/requirements.txt agent/requirements.txt
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r agent/requirements.txt -r backend/requirements.txt

COPY . .

WORKDIR /app/frontend
RUN npm install && npm run build
WORKDIR /app

RUN npx -y mongodb-mcp-server@latest || true

EXPOSE 8000

ENV AGENT_SERVICE_URL=http://localhost:8001

CMD ["python", "start_hf.py"]
