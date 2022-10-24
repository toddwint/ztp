FROM toddwint/mybaseimage
COPY app /opt/ztp
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    HTTPPORT1=8080 \
    HTTPPORT2=8081 \
    HTTPPORT3=8082 \
    HTTPPORT4=8083 \
    HUID=1001 \
    HGID=1001 \
    HOSTNAME=ztpsrvr \
    APPNAME=ztp
RUN apt-get update \
    && \
    apt-get install -y \
    rsyslog \
    isc-dhcp-server \
    ftp \
    vsftpd \
    tftp-hpa \
    tftpd-hpa \
    webfs \
    && \
    echo $HOSTNAME > /etc/hostname \
    && \
    cd /opt \
    && \
    rm -rf /opt/mybaseimage \
    && \
    apt-get autoremove -y \
    && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ztp/debug
CMD ["/opt/ztp/scripts/startup.sh"]
