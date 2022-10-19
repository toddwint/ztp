#!/usr/bin/env bash
set -x
ps ax -eo pid,lstart,cmd | grep vsftpd:
