#!/usr/bin/env bash

TS=$(date -Is | tr -d :)
REPORT_GLOB="/opt/$APPNAME/ftp/transfer_report-*.csv"
XFER_REPORT="/opt/$APPNAME/logs/transfer_report.csv"
HUID=$(id --user "$APPNAME" 2> /dev/null || id --user root)
HGID=$(id --group "$APPNAME" 2> /dev/null || id --group root)

if [ ! -f "$XFER_REPORT" ]; then
    echo "$XFER_REPORT does not exist."
    exit 1
fi

# Check if current xfer report is the same as any previous exports
hash_xfer_report=$(md5sum $XFER_REPORT | awk '{print $1}')
hash_previous_search=$(md5sum $REPORT_GLOB | grep $hash_xfer_report)
RETURN=$?
if [ $RETURN -eq 0 ]; then
    echo "Transfer report export will be skipped." \
        "It is idential to another report."
    exit 1
fi

# check if current xfer report has data after column 5
has_data=$(\
    sed '1d' $XFER_REPORT \
    | cut --delimiter=, --fields=6- \
    | grep -E '\w+' \
    )
RETURN=$?
if [ $RETURN -eq 0 ]; then
    echo "Transfer report contains transfers. Exporting current report..."
    xfer_export=/opt/"$APPNAME"/ftp/transfer_report-"${TS}".csv
    cp /opt/"$APPNAME"/ftp/transfer_report.csv $xfer_export
    chown $HUID:$HGID $xfer_export
    echo "Transfer report saved to \`./ftp/transfer_report-"${TS}".csv\`"
else
    echo "Transfer report export will be skipped." \
    "It does not contain any transfer data."
    exit 1
fi
