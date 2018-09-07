#!/bin/bash

source /opt/workshop/bin/activate

if [ x"$JUPYTERHUB_USER" != x"" ]; then
    URI_ROOT_PATH=/user/$JUPYTERHUB_USER
else
    URI_ROOT_PATH=/user/default
fi

export URI_ROOT_PATH

cd /opt/workshop

exec python /opt/workshop/app.py
