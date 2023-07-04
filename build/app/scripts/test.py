#!/usr/bin/env python3

import pathlib

appname='ztp'
#dhcp_report_template = f'/opt/{appname}/configs/dhcp_report.csv.template'
#dhcp_report_template = pathlib.Path(dhcp_report_template)

_ = pathlib.Path(f'/opt/{appname}/configs/dhcp_report.csv.template')
dhcp_report_template = _
