from util import path

import sys, time
from BluenetLib import Bluenet, BluenetEventBus, UsbTopics, Util
from util.util import programCrownstone, findUsbBleDongleHciIndex, findUartAddress

bluenet = Bluenet(catchSIGINT=True)

def initLibs():
    import traceback
    try:
        address = findUartAddress()
        if address == False:
            print("Could not find Crownstone")
        else:
            bluenet.initializeUSB(address)  # TODO: get tty address dynamically
    except:
        print("----- ----- Error in settings UART Address", sys.exc_info()[0])
        traceback.print_exc()
        print("tester not working, reboot test")



def enableUart():
    # enable UART
    print("----- Enabling UART...")
    bluenet._usbDev.setUartMode(3)



initLibs()

time.sleep(1)

enableUart()

while True:
    time.sleep(0.2)