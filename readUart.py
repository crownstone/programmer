from crownstone_uart import CrownstoneUart

from util import path

import sys, time
from util.util import programCrownstone, findUsbBleDongleHciIndex, findUartAddress

uart = CrownstoneUart()

def initLibs():
    import traceback
    try:
        address = findUartAddress()
        if address == False:
            print("Could not find Crownstone")
        else:
            uart.initialize_usb_sync(address)
    except:
        print("----- ----- Error in settings UART Address", sys.exc_info()[0])
        traceback.print_exc()
        print("tester not working, reboot test")



def enableUart():
    # enable UART
    print("----- Enabling UART...")
    uart._usbDev.setUartMode(3)



initLibs()

time.sleep(1)

enableUart()

while True:
    time.sleep(0.2)