#!/bin/sh

if [ -n "$PDA_SERVICE_HOST" ]
then
    PDA_HOSTNAME="http://"$PDA_SERVICE_HOST
else
    PDA_HOSTNAME="http://127.0.0.1"
fi

if [ -n "$PDA_SERVICE_PORT" ]
then
    PDA_CONSOLE_PORT=$PDA_SERVICE_PORT
fi


PARAMETERS=""
if [ -n "$PDA_CONSOLE_PORT" ]
then
    PARAMETERS="$PARAMETERS PDA_CONSOLE_PORT=$PDA_CONSOLE_PORT"
    service apache2 stop
    sed -i "s/^Listen .*/Listen $PDA_CONSOLE_PORT/" /etc/apache2/ports.conf
else
    PDA_CONSOLE_PORT="8999"
fi

service rsyslog start
logger "Starting Predictive Data Adapter container: $PARAMETERS"

# prepare folders for pda_api
mkdir -p /opt/prophetstor/alameter/var/
mkdir -p /var/log/apache2/
chgrp www-data /opt/prophetstor/alameter/var/
chmod 775 /opt/prophetstor/alameter/var/
chmod 775 /var/log/apache2/
env > /opt/prophetstor/alameter/alameter.env

# start http server for GUI and API
service apache2 start

while [ 1 ]
do
    echo -n "."
    sleep 10
done
