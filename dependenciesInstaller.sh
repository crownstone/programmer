#!/bin/bash

# install python 3.7 dependencies (should already be there due to the python37Installer)
sudo apt-get update -y
sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y

# install python lib dependencies
sudo apt-get install build-essential libbluetooth-dev libglib2.0-dev python3-setuptools

