FROM jupyter/scipy-notebook:latest
ENV HTTP_PROXY http://cache-adm:8080
ENV HTTPS_PROXY http://cache-adm:8080
ENV http_proxy http://cache-adm:8080
ENV https_proxy http://cache-adm:8080
RUN apt-get -y install build-essential
RUN pip install --upgrade pip
RUN pip install crillab-metrics