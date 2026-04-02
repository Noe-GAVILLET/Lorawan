FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY model/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY model /app/model

CMD ["python", "model/random_data_publisher.py"]
