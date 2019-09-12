#!/bin/bash
#

jack_control start
jack_control ds alsa
jack_control dps device hw:USB
jack_control dps rate 48000
jack_control dps nperiods 2
jack_control dps period 512
sleep 3

echo "STARTED AT $(date)" >> /home/keller/.jack-status

mixxx


jack_control stop

echo "STOPPED AT $(date)" >> /home/keller/.jack-status
