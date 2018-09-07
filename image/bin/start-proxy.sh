#!/bin/bash

set -eo pipefail

set -x

if [ x"$JUPYTERHUB_USER" != x"" ]; then
    URI_ROOT_PATH=/user/$JUPYTERHUB_USER
else
    URI_ROOT_PATH=/user/default
fi

export URI_ROOT_PATH

cd /opt/workshop

exec node /opt/workshop/proxy.js
