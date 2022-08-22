#!/usr/bin/env bash

echo -e 'Stopping frontail...'

kill $(pidof frontail)
