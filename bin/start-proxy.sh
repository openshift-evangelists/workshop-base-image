#!/bin/bash

set -eo pipefail

set -x

if [ x"$JUPYTERHUB_SERVICE_PREFIX" != x"" ]; then
    URI_ROOT_PATH=${JUPYTERHUB_SERVICE_PREFIX%/}
else
    URI_ROOT_PATH=/user/default
fi

export URI_ROOT_PATH

cd /opt/workshop

exec node /opt/workshop/proxy.js
