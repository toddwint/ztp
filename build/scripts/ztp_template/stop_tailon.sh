#!/usr/bin/env bash

if [ ! -z "$(pidof tailon)" ]
then
    echo -e 'Stopping tailon...'
    kill -9 $(pidof tailon)
else
    echo -e 'tailon is not running.'
fi
