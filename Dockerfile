FROM python:3.8.0
ENV HTTP_PROXY http://cache-adm:8080
ENV HTTPS_PROXY http://cache-adm:8080
ENV http_proxy http://cache-adm:8080
ENV https_proxy http://cache-adm:8080
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -y install build-essential
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
RUN make test