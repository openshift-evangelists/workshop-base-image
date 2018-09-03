#!/bin/bash

set -a
. /opt/terminal/etc/envvars
set +a

export SHELL=/bin/bash
export PS1="[$JUPYTERHUB_USER:\w] $ "

exec /bin/bash "$@"
