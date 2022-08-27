#!/usr/bin/env bash

# frontail has a subprocess of tail
if [ ! -z "$(pidof tail)" ]
then
    kill $(pidof tail)
fi

if [ ! -z "$(pidof frontail)" ]
then
    echo -e 'Stopping frontail...'
    kill -9 $(pidof frontail)
else
    echo -e 'frontail is not running.'
fi
