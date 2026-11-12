FROM python:3.11-slim
WORKDIR /app
COPY lab8.py .
CMD ["python", "lab8.py"]