FROM ubuntu:16.04
MAINTAINER Albert Lin <albert.lin@prophetstor.com>

# Install system utilities
RUN sed -i'' 's/archive\.ubuntu\.com/us\.archive\.ubuntu\.com/' /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    iputils-ping \
    rsyslog \
    net-tools \
    vim \
    wget \
    curl \
    openssh-client \
    sqlite3 \
    php \
    php-curl \
    apache2 \
    libapache2-mod-php \
    libapache2-mod-wsgi \
    python-flask \
    python-flask-restful \
    python-flask-httpauth \
    python-requests \
    python-influxdb

# Install PDA GUI
ADD build/api /opt/prophetstor/alameter/api
ADD httpd.conf /etc/apache2/sites-enabled/alameter.conf

ENV PDA_CONSOLE_PORT 8999
ADD start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT ["/start.sh"]
