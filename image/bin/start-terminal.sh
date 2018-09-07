#!/bin/bash

set -a
. /opt/workshop/etc/envvars
set +a

export SHELL=/bin/bash
export PS1="[$JUPYTERHUB_USER:\w] $ "

exec /bin/bash "$@"
