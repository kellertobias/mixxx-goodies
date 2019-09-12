#!/bin/bash
DEVICE=$(lsusb -d 1235:0018)
DEVICE=($DEVICE)

USB_BUS=${DEVICE[1]}
USB_DEV=${DEVICE[3]}
USB_DEV=$(echo $USB_DEV | sed 's/:*$//g')

docker run -ti --rm \
	-e DISPLAY=$DISPLAY \
	--privileged \
    --cap-add SYS_PTRACE \
	--device=/dev/bus/usb/$USB_BUS/$USB_DEV \
	--volume /tmp/.X11-unix:/tmp/.X11-unix \
	--volume /home/keller/Google\ Drive/Musik/:/home/$USER/Google\ Drive/Musik/ \
	mixxx
# Bus 005 Device 005: ID 1235:0018 Focusrite-Novation Twitch
# --device=/dev/ttyUSB0 \
