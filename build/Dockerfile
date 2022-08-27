FROM ubuntu:jammy
COPY scripts /opt/ztp/scripts
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    HTTPPORT=8000 \
    HOSTNAME=ztpsvr01 \
    SUBNET=192.168.1.0/24 \
    GATEWAY=192.168.1.1 \
    HUID=1001 \
    HGID=1001
RUN apt-get update \
    && \
    apt-get install -y \
    ftp \
    iproute2 \
    isc-dhcp-server \
    python3 \
    rsyslog \
    tftp \
    tftpd-hpa \
    tzdata \
    vsftpd \
    wget \
    && \
    wget -q https://github.com/mthenw/frontail/releases/download/v4.9.1/frontail-linux -O /usr/local/bin/frontail \
    && \
    chmod 775 /usr/local/bin/frontail \
    && \
    gzip /usr/local/bin/frontail \
    && \
    wget -q https://github.com/gvalkov/tailon/releases/download/v1.1.0/tailon_1.1.0_linux_amd64.tar.gz -O /usr/local/bin/tailon_1.1.0_linux_amd64.tar.gz \
    && \
    tar -C /usr/local/bin -xvf /usr/local/bin/tailon_1.1.0_linux_amd64.tar.gz tailon \
    && \
    rm /usr/local/bin/tailon_1.1.0_linux_amd64.tar.gz \
    && \
    chmod 775 /usr/local/bin/tailon \
    && \
    gzip /usr/local/bin/tailon \
    && \
    apt-get remove -y \
    wget \
    && \
    apt-get autoremove -y \
    && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ztp/scripts
CMD ["/opt/ztp/scripts/startup.sh"]
