#!/bin/sh
# call from /etc/logrotate.d/rsyslog

cd /opt/matomo
. .venv/bin/activate
python matomo-import.py --url=https://matomo.text-analytics.ch --token-auth=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx --log-format-name opnsense
