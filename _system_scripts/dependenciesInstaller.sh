#!/bin/bash

apt-get update
apt-get upgrade

# install python lib dependencies
apt-get install cifs-utils build-essential libbluetooth-dev libglib2.0-dev python3-setuptools bzip2 libbz2-dev libreadline6 libreadline6-dev libffi-dev libssl1.0-dev sqlite3 libsqlite3-dev -y
