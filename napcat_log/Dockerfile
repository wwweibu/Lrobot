FROM docker.m.daocloud.io/library/python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY log.py .
CMD ["python", "log.py"]