FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 10001 lab
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /data/firmware && chown -R lab:lab /data /app
USER lab
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--timeout", "120", "app.server:app"]
