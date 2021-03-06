import sys, os
from pathlib import Path
import subprocess
import time, signal
import traceback

from config import MOUNT_PATH, NAME_OF_USB_DONGLE, STATE_MANAGER_PATH


def checkMedia():
    for item in os.listdir(MOUNT_PATH):
        if os.path.isdir(MOUNT_PATH + "/" + item):
            if item == NAME_OF_USB_DONGLE:
                filesOnDrive = os.listdir(MOUNT_PATH + NAME_OF_USB_DONGLE)
                if len(filesOnDrive) > 0:
                    return True
    return False

codeUsbDongleConnected = checkMedia()
print("State of USB:", codeUsbDongleConnected)

class ProggerManager:
    session = None
    running = False

    def __init__(self):
        pass


    def disconnectedCodeDrive(self):
        self.cleanup()


    def connectedCodeDrive(self):
        if not self.running:
            self.running = True
            # start all processes. LED is on. Button is listened to!
            self.runCode()


    def runCode(self):
        print("UsbWatcher: Starting subprocess")
        self.session = subprocess.Popen(["sudo", "python3", STATE_MANAGER_PATH], preexec_fn=os.setsid)


    def cleanup(self):
        # kill all processes. LED goes off. Button is ignored!
        print("UsbWatcher: Kill ProggerStateManager process")
        self.running = False
        if self.session is not None:
            print("UsbWatcher: Terminating ProggerStateManager")
            try:
                self.session.terminate()
            except:
                print("UsbWatcher: Error terminating ProggerStateManager", sys.exc_info()[0])
                traceback.print_exc()
            try:
                print("UsbWatcher: Waiting to terminate ProggerStateManager")
                self.session.wait(5)
                print("UsbWatcher: ProggerStateManager has been Terminated.")
            except:
                traceback.print_exc()
                print("UsbWatcher: Terminate not successful. Killing ProggerStateManager now.", sys.exc_info()[0])
                if self.session is not None:
                    self.session.kill()
                time.sleep(3)

            self.session = None
        else:
            print("UsbWatcher: I dont have a session!")


theManager = ProggerManager()

running = True

def cleanup(source=None, frame=None):
    theManager.cleanup()
    running = False
    time.sleep(1)
    quit()

signal.signal(signal.SIGINT,  cleanup)
signal.signal(signal.SIGTERM, cleanup)


if codeUsbDongleConnected:
    theManager.connectedCodeDrive()

while running:
    measurement = checkMedia()
    time.sleep(0.5)
    if codeUsbDongleConnected:
        codeUsbDongleConnected = measurement
        if not codeUsbDongleConnected:
            print("UsbWatcher: USB dongle has been disconnected. Closing child processes....")
            theManager.disconnectedCodeDrive()
    else:
        codeUsbDongleConnected = measurement
        if codeUsbDongleConnected:
            print("UsbWatcher: USB dongle has been Connected! Starting ProggerStateManager!")
            theManager.connectedCodeDrive()
        else:
            subprocess.Popen(["sudo", "mount", "-a"], preexec_fn=os.setsid)

