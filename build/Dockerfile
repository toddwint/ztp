FROM toddwint/mybaseimage
COPY app /opt/ztp
LABEL LICENSE="GPL-3.0-or-later"
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    HTTPPORT1=8080 \
    HTTPPORT2=8081 \
    HTTPPORT3=8082 \
    HTTPPORT4=8083 \
    HUID=0 \
    HGID=0 \
    HOSTNAME=ztpsrvr \
    APPNAME=ztp
RUN apt-get update \
    && \
    apt-get install -y \
    rsyslog \
    isc-dhcp-server \
    ftp \
    ntp \
    vsftpd \
    tftp-hpa \
    tftpd-hpa \
    webfs \
    #util-linux \
    bsdmainutils \
    fzf \
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
