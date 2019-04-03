#!/bin/bash

tar -C /home/pi/ -xvf /media/programmer_code_dongle/_system_scripts/JLink_Linux_V642c_arm.tgz
sudo cp /home/pi/JLink_Linux_V642c_arm/99-jlink.rules /etc/udev/rules.d/
sudo cp -r /home/pi/JLink_Linux_V642c_arm/* /usr/bin
rm -r /home/pi/JLink_Linux_V642c_arm

cp /media/programmer_code_dongle/config.py /home/pi/
cp /media/programmer_code_dongle/UsbWatcher.py /home/pi/
cp /media/programmer_code_dongle/_system_scripts/watcherStart.sh /home/pi/
chmod a+x /home/pi/watcherStart.sh

# make service
mkdir -p /home/pi/.config/systemd/user/
cp /media/programmer_code_dongle/_system_scripts/crownstone.service /home/pi/.config/systemd/user/
chmod a-x /home/pi/.config/systemd/user/crownstone.service
echo "Enable crownstone service"
systemctl --user enable crownstone
echo "Reboot"
sudo reboot

