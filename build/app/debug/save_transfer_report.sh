#!/usr/bin/env bash
#set -x
TS=$(date -Is | tr -d :)
/opt/"$APPNAME"/scripts/generate_transfer_report.py

REPORT_GLOB="/opt/$APPNAME/ftp/transfer_report-*.csv"
XFER_REPORT="/opt/$APPNAME/ftp/transfer_report.csv"

if [ ! -f "$XFER_REPORT" ]
    then
    echo "$XFER_REPORT does not exist."
    exit 1
fi

if compgen -G $REPORT_GLOB > /dev/null
then
    # One or more previous export(s) exist
    PREV_REPORT=$(ls $REPORT_GLOB | tail -n1)
    DIFF=$(diff -s $XFER_REPORT $PREV_REPORT)
    RETURN=$?
    if [ $RETURN -eq 0 ]
    then
        echo "Transfer report export will be skipped because $PREV_REPORT is identical to $XFER_REPORT."
        exit 1
    else
        echo "Previous export is different than current report. Exporting current report..."
        # The files are different so an export is needed.
    fi
else
    echo "No previous report export found. Creating one..."
    # No previous files exist so an export is needed.
fi

cp /opt/"$APPNAME"/ftp/transfer_report.csv \
   /opt/"$APPNAME"/ftp/transfer_report-"${TS}".csv
chown $HUID:$HGID /opt/"$APPNAME"/ftp/transfer_report-"${TS}".csv
echo "Transfer report saved to \`./ftp/transfer_report-"${TS}".csv\`"
