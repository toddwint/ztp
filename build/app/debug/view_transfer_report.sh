#!/usr/bin/env bash
set -x
/opt/"$APPNAME"/scripts/generate_transfer_report.py
column -ts, /opt/"$APPNAME"/ftp/transfer_report.csv
