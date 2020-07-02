FROM python:3.8.3-slim-buster
COPY . /app
WORKDIR /app
RUN python -m pip install -r requirements.txt
EXPOSE 8080
CMD ["gunicorn"  , "-b", "0.0.0.0:8080", "wsgi:application"]
