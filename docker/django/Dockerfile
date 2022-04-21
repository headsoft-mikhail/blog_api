FROM python:3.8.10-slim
WORKDIR /usr/src/app

EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt .
RUN ["pip", "install", "-U", "pip"]
RUN ["pip", "install", "-r", "requirements.txt"]
RUN ["pip", "install", "psycopg2-binary==2.9.3", "gunicorn==20.1.0"]

COPY . .
CMD ["sh", "./start.sh"]
