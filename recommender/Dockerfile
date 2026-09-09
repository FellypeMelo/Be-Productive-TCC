FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
USER app
EXPOSE 8002
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8002"]
