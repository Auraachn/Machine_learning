FROM python:3.9

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./


RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 0 --app:app