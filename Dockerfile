FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY frontend/ frontend/
WORKDIR /build/frontend
RUN npm install && npm run build

FROM python:3.12-slim

# Node is required at runtime for the MongoDB MCP Server (npx mongodb-mcp-server)
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build/frontend/dist /app/frontend/dist

COPY backend/ backend/
COPY start_hf.py .

EXPOSE 8000

CMD ["python", "start_hf.py"]
