#!/bin/bash

set -a
. /opt/terminal/etc/profile.d/sh.terminal
set +a

export SHELL=/bin/bash
export PS1="[$JUPYTERHUB_USER:\w ] $ "

exec /bin/bash "$@"
