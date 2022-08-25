FROM ubuntu:jammy
COPY scripts /opt/ztp/scripts
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    HTTPPORT=8080 \
    HOSTNAME=ztpsrvr01 \
    SUBNET=192.168.1.0/24 \
    GATEWAY=192.168.1.1 \
    HUID=1000 \
    HGID=1000
RUN apt-get update \
    && \
    apt-get install -y \
    ftp \
    iproute2 \
    isc-dhcp-server \
    python3 \
    python3-pip \
    rsyslog \
    tftp \
    tftpd-hpa \
    tzdata \
    vsftpd \
    wget \
    && \
    pip3 install netaddr \
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
    python3-pip \
    wget \
    && \
    apt-get autoremove -y \
    && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ztp/
CMD ["/opt/ztp/scripts/startup.sh"]
