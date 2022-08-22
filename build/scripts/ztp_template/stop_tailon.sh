#!/usr/bin/env bash

echo -e 'Stopping tailon...'

kill $(pidof tailon)
