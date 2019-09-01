#!/bin/bash
#
#This script starts a jackd audio server.
#
#I am using Pulseaudio for entertainment and system audio on top of jack
#and another output on my soundcard for MIXXX and my DAW
#


jack_control start
jack_control ds alsa
jack_control dps device hw:USB
jack_control dps rate 48000
jack_control dps nperiods 2
jack_control dps period 512
# sleep 10
# a2jmidid -e &
# sleep 10
# qjackctl &
pacmd unload-module module-udev-detect 
sleep 3
pacmd set-default-sink jack_out

echo "STARTED AT $(date)" >> /home/keller/.jack-status
