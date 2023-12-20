FROM python:3.9-slim

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD exec gunicorn --bind :5000 --workers 1 --threads 0 main:app
