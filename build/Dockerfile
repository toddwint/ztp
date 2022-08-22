FROM ubuntu:jammy
COPY scripts /opt/ztp/scripts
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    HTTPPORT=8080 \
    HOSTNAME=ztpsrvr01
RUN apt-get update \
    && \
    apt-get install -y \
    tzdata \
    iproute2 \
    gawk \
    wget \
    python3 \
    ipcalc \
    isc-dhcp-server \
    vsftpd \
    tftpd-hpa \
    tftp \
    ftp \
    rsyslog \
    && \
    wget -q https://github.com/mthenw/frontail/releases/download/v4.9.1/frontail-linux -O /usr/local/bin/frontail \
    && \
    chmod 755 /usr/local/bin/frontail \
    && \
    wget -q https://github.com/gvalkov/tailon/releases/download/v1.1.0/tailon_1.1.0_linux_amd64.tar.gz -O /usr/local/bin/tailon_1.1.0_linux_amd64.tar.gz \
    && \
    tar -C /usr/local/bin -xvf /usr/local/bin/tailon_1.1.0_linux_amd64.tar.gz tailon \
    && \
    rm /usr/local/bin/tailon_1.1.0_linux_amd64.tar.gz \
    && \
    chmod 755 /usr/local/bin/tailon \
    && \
    apt-get remove -y \
    wget \
    && \
    apt-get autoremove -y \
    && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ztp/
CMD ["/opt/ztp/scripts/startup.sh"]
