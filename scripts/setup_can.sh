#!/bin/bash
if [[ $1 == *"vcan"*  ]]; then
    sudo modprobe vcan
    sudo ip link add dev $1 type vcan
    sudo ip link set up $1
else
    sudo ifconfig $1 down
    sudo ip link set $1 type can bitrate 500000
    sudo ip link set $1 up
    sudo ifconfig $1 txqueuelen 65535
fi

sudo ip link set $1 txqueuelen 100000
sudo ip -details -statistics link show $1 
