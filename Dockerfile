FROM python:3.13-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY content /app/content
COPY src /app/src
COPY static /app/static
COPY templates /app/templates

EXPOSE 8027

CMD ["python3", "/app/src/run.py"]
