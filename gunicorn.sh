cd /usr/src/app/
gunicorn metrics.studio.web.application:server -b 0.0.0.0:8000