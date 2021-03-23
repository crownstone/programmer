#!/bin/bash

apt-get update
apt-get upgrade

# install python lib dependencies
apt-get install python3-dev python3-rpi.gpio -y
