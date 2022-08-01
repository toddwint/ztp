#!/usr/bin/env bash

echo -e 'Stopping frontail-linux...'

kill $(pidof frontail)
