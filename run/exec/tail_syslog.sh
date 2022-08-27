#!/usr/bin/env bash
source "$(dirname "$(dirname "$(realpath $0)")")"/config.txt

# note: The `-it` options are needed. When CTRL-C is used
#       to kill the tail -f command, it kills the tail
#       process instead of just the docker bash script.
# -i, --interactive[=false]    Keep STDIN open even if not attached
# -t, --tty[=false]            Allocate a pseudo-TTY

docker exec -it "$HOSTNAME" tail -n 33 -f /var/log/syslog
