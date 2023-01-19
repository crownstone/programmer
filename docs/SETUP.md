# Prepare a Raspberry Pi for the programmer

- Use the [Rasperry Pi imager](https://www.raspberrypi.com/news/raspberry-pi-imager-imaging-utility/) to create an SD card.
    - OS: Raspbian Stretch Lite (Raspberry Pi OS Lite legacy, port of Debian Buster), a newer version will probably work too.
    - Configure the login.
- Boot the Raspberry Pi with the SD card.
- Find the IP of the Raspberry Pi:
    ```
    sudo nmap -sn 10.27.8.0/24 | grep -r Raspberry -B 3
    ```
- Enable ssh and auto login via: `raspi-config`
- Copy the contents of this repository to the USB drive.
- Get the USB drive to mount.
    - Go to `/etc/fstab` and add this line:
        ```
        LABEL=PROGGERCODE       /media/programmer_code_dongle      vfat    defaults,noatime,nofail,ro      0       0
        ```
- Set the config file to get the pin layout of your progger:
    ```
    echo 2 > ~/programmer_pin_version
    ```
    - Set the 2 to the matching number. You can find the supported maps in `repo/lib/GpioMap`.
- Reboot: `sudo reboot now`
- Insert the USB drive and run:
    ```
    sudo /media/programmer_code_dongle/_system_scripts/dependenciesInstaller.sh
    source /media/programmer_code_dongle/_system_scripts/copyOps.sh
    ```
    There will be a reboot.
- Ensure that the service starts on boot without ssh.
- Finally, when everything has been tested REALLY WELL, run the read-only-fs.sh in the danger folder:
    ```
    sudo /media/programmer_code_dongle/_system_scripts/danger/read-only-fs.sh
    ```