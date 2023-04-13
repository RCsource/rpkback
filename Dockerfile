FROM python:3.11-slim
ENV PYTHONUNBUFFERED=true
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
RUN rm requirements.txt

CMD uvicorn rpkback:app --host 0.0.0.0 --port 8080
