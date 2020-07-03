FROM python:3.8.3-slim-buster
COPY . /app
WORKDIR /app
ENV PATH="$PATH:/opt/vc/bin"
RUN echo "/opt/vc/lib" > /etc/ld.so.conf.d/00-vcms.conf
RUN python -m pip install -r requirements.txt
EXPOSE 8080
CMD ["ldconfig", "&&", "gunicorn"  , "-b", "0.0.0.0:8080", "wsgi:application"]
