#!/bin/bash

set -eo pipefail

set -x

if [ x"$JUPYTERHUB_USER" != x"" ]; then
    URI_ROOT_PATH=/user/$JUPYTERHUB_USER
else
    URI_ROOT_PATH=/user/default
fi

# Now execute the program. We need to supply a startup script for the
# shell to setup the environment.

MOTD_FILE=motd

if [ -f /opt/workshop/etc/motd ]; then
    MOTD_FILE=/opt/workshop/etc/motd
fi

if [ -f /opt/app-root/etc/motd ]; then
    MOTD_FILE=/opt/app-root/etc/motd
fi

exec /opt/workshop/bin/butterfly.server.py --port=8082 \
    --host=0.0.0.0 --uri-root-path="$URI_ROOT_PATH/terminal" --unsecure \
    --i-hereby-declare-i-dont-want-any-security-whatsoever \
    --shell=/opt/workshop/bin/start-terminal.sh --motd=$MOTD_FILE
