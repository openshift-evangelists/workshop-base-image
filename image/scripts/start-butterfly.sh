#!/bin/bash

set -eo pipefail

set -x

BUTTERFLY_URL_PREFIX=${BUTTERFLY_URL_PREFIX:-}
BUTTERFLY_SERVER_PORT=${BUTTERFLY_SERVER_PORT:-8080}

# Now execute the program. We need to supply a startup script for the
# shell to setup the environment.

MOTD_FILE=motd

if [ -f /opt/terminal/etc/motd ]; then
    MOTD_FILE=/opt/terminal/etc/motd
fi

if [ -f /opt/app-root/etc/motd ]; then
    MOTD_FILE=/opt/app-root/etc/motd
fi

exec /opt/terminal/bin/butterfly.server.py --port=$BUTTERFLY_SERVER_PORT \
    --host=0.0.0.0 --uri-root-path="$BUTTERFLY_URL_PREFIX" --unsecure \
    --i-hereby-declare-i-dont-want-any-security-whatsoever \
    --shell=/opt/terminal/bin/start-terminal.sh --motd=$MOTD_FILE
