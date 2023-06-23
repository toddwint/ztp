#!/usr/bin/env bash
#set -x
TS=$(date -Is | tr -d :)
/opt/"$APPNAME"/scripts/generate_transfer_report.py
cp /opt/"$APPNAME"/ftp/transfer_report.csv \
   /opt/"$APPNAME"/ftp/transfer_report-"${TS}".csv
chown $HUID:$HGID /opt/"$APPNAME"/ftp/transfer_report-"${TS}".csv
echo "Transfer report saved to \`/ftp/transfer_report-"${TS}".csv\`"
