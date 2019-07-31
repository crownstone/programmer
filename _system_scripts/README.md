# Preperation

Assuming a blank lite image from raspbian:

- get the USB dongle to mount.
    - Go to /etc/fstab and add this line:
        ```
        LABEL=PROGGERCODE       /media/programmer_code_dongle      vfat    defaults,noatime,nofail,ro      0       0
        ```
   
    
- set the environment variable to match the pin layout of your progger:
    - go the /etc/environment and add this line:
        ```
        PROGGER_PIN_LAYOUT_VERSION="2"

        ```
    - Set the 2 to the matching number. You can find the supported maps in repo/lib/GpioMap
    
    
- reboot
    
- insert the USB drive and run 
    ```
    sudo /media/programmer_code_dongle/_system_scripts/dependenciesInstaller.sh
    ```
- then run 
    ```
    source /media/programmer_code_dongle/_system_scripts/copyOps.sh
    ```
    There will be a reboot.

- finally, when everything has been tested REALLY WELL, run the read-only-fs.sh in the danger folder
    ```
    sudo /media/programmer_code_dongle/_system_scripts/danger/read-only-fs.sh
    ```