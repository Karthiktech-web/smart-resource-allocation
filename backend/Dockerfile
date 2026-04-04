FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . .

# Install FastAPI & Uvicorn (basic run)
RUN pip install fastapi uvicorn

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]