FROM ubuntu:bionic

RUN apt update && apt upgrade -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:mixxx/mixxx && apt update
RUN apt install -y mixxx jackd alsa usbutils sudo

RUN export uid=1000 gid=1000 && \
    mkdir -p /home/keller && \
    echo "keller:x:${uid}:${gid}:keller,,,:/home/keller:/bin/bash" >> /etc/passwd && \
    echo "keller:x:${uid}:" >> /etc/group && \
    chown ${uid}:${gid} -R /home/keller
RUN dbus-uuidgen > /var/lib/dbus/machine-id && \
    mkdir -p /var/run/dbus && \
	dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address

ADD scripts/start-mixxx.docker.sh /mixxx/start.sh
RUN chmod +x /mixxx/*

RUN usermod -a -G audio keller && \
    usermod -a -G device keller  && \
    usermod -a -G plugdev keller  && \
    usermod -a -G adm keller  && \
    usermod -a -G dialout keller  && \
    usermod -a -G cdrom keller  && \
    usermod -a -G sudo keller  && \
    usermod -a -G dip keller  && \
    usermod -a -G lpadmin keller
USER keller
ENV HOME /home/keller
RUN mkdir -p /home/keller/Google\ Drive/Musik/ && \
    ln -s /home/keller/Google\ Drive/Musik/.mixxx /home/keller/.mixxx

CMD [ "/mixxx/start.sh" ]
