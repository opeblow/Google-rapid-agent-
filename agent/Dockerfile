FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /agent

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN npx -y mongodb-mcp-server@latest || true

EXPOSE 8001

CMD python seed.py ; uvicorn agent_server:app --host 0.0.0.0 --port ${PORT:-8001}
