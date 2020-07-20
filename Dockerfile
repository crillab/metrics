FROM python:latest
ENV HTTP_PROXY http://cache-adm:8080
ENV HTTPS_PROXY http://cache-adm:8080
ENV http_proxy http://cache-adm:8080
ENV https_proxy http://cache-adm:8080
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app/

RUN chmod +x ./gunicorn.sh

EXPOSE 8000

#ENTRYPOINT ['./gunicorn.sh']