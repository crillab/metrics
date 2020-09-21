#!/bin/sh

NAME="metrics"                                  # Name of the application
APPDIR=/home/metrics/metrics-master             # App project directory
app="metrics.studio.web.application:server"
NUM_WORKERS=1                                     # how many worker processes should Gunicorn spawn
LOGDIRS="$APPDIR/logs"

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $APPDIR || exit
export PYTHONPATH=$APPDIR:$PYTHONPATH

# Create the log directory if it doesn't exist
test -d $LOGDIRS || mkdir -p $LOGDIRS

touch $LOGDIRS/gunicorn.log

echo "gunicorn $APP --name $NAME --workers $NUM_WORKERS --log-level=debug --log-file=$LOGDIRS/logs/gunicorn.log"
# Start your app with gunicorn
# $APPDIR/venv/bin/gunicorn $app --name $NAME --workers $NUM_WORKERS --bind=127.0.0.1:8000 --log-level=debug --log-file=$LOGDIRS/gunicorn.log --daemon
$APPDIR/venv/bin/gunicorn $app --name $NAME --workers $NUM_WORKERS --bind=127.0.0.1:8000 --log-level=debug --log-file=$LOGDIRS/gunicorn.log
