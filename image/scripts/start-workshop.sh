#!/bin/bash

source /opt/terminal/bin/activate

if [ x"$JUPYTERHUB_USER" != x"" ]; then
    URI_ROOT_PATH=/user/$JUPYTERHUB_USER
else
    URI_ROOT_PATH=/user/default
fi

export URI_ROOT_PATH

export FLASK_APP=/opt/terminal/workshop/application.py

exec flask run --port 8081
