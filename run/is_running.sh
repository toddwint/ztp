#!/usr/bin/env bash
source "$(dirname "$(realpath $0)")"/config.txt
running=$(docker ps | grep "$HOSTNAME" | wc -l)
if [ $running -eq 1 ]
then
    echo "Yes. It is running. Look:  "
    docker ps | grep "$HOSTNAME"
else
    echo "He's dead Jim."
fi
