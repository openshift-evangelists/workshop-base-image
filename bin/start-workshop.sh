#!/bin/bash

source /opt/workshop/bin/activate

if [ x"$JUPYTERHUB_SERVICE_PREFIX" != x"" ]; then
    URI_ROOT_PATH=${JUPYTERHUB_SERVICE_PREFIX%/}
else
    URI_ROOT_PATH=/user/default
fi

export URI_ROOT_PATH

cd /opt/workshop

export PYTHONPATH=/opt/workshop

exec python /opt/workshop/app.py
