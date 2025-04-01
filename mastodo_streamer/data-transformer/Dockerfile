FROM python:3.9-slim

WORKDIR /app

COPY update_analytics.py .
COPY requirements.txt .
COPY scheduler.py .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install schedule

CMD ["python", "-u", "scheduler.py"]
