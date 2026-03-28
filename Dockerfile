FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data volume mount point
RUN mkdir -p /data

# Environment
ENV ENVIRONMENT=production
ENV DATABASE_URL=sqlite:////data/klara.db
ENV PORT=8000

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; r=requests.get('http://localhost:${PORT}/greenhouse/health'); exit(0 if r.status_code==200 else 1)"

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
