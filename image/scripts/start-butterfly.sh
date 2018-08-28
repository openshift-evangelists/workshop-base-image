#!/bin/bash

set -eo pipefail

set -x

URI_ROOT_PATH=${URI_ROOT_PATH:-}

# The butterfly application has a bug whereby if the config file is
# not present, it will ignore the --uri-root-path option, so create
# the file if it doesn't exist.

mkdir -p $HOME/.config/butterfly
touch $HOME/.config/butterfly/butterfly.conf

# Now execute the program. We need to supply a shell script for the
# shell to setup the environment.

oc config set-cluster local --server "https://$KUBERNETES_PORT_443_TCP_ADDR"
oc config set-context me --cluster local --user "$JUPYTERHUB_USER"
oc config use-context me

MOTD_FILE=motd

if [ -f /opt/terminal/etc/motd ]; then
    MOTD_FILE=/opt/terminal/etc/motd
fi

if [ -f $HOME/.config/butterfly/motd ]; then
    MOTD_FILE=$HOME/.config/butterfly/motd
fi

exec /opt/terminal/bin/butterfly.server.py --port=8080 \
    --host=0.0.0.0 --uri-root-path="$URI_ROOT_PATH" --unsecure \
    --i-hereby-declare-i-dont-want-any-security-whatsoever \
    --shell=/opt/terminal/bin/start-terminal.sh --motd=$MOTD_FILE
