# from util import path

from crownstone_uart.topics.DevTopics import DevTopics
from crownstone_uart import CrownstoneUart, UartEventBus
import sys, time, logging
# from util.util import programCrownstone, findUsbBleDongleHciIndex, findUartAddress

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


uart = CrownstoneUart()

def initLibs():
    # import traceback
    # try:
    #     address = findUartAddress()
    #     if address == False:
    #         print("Could not find Crownstone")
    #     else:
    uart.initialize_usb_sync()
    # except:
    #     print("----- ----- Error in settings UART Address", sys.exc_info()[0])
    #     traceback.print_exc()
    #     print("tester not working, reboot test")



def enableUart():
    # enable UART
    print("----- Enabling UART...")
    uart._usbDev.setUartMode(3)


def _getMacAddress():
    result = [True, None]

    def handleMessage(container, data):
        container[0] = False
        container[1] = data

    subscriptionId = UartEventBus.subscribe(DevTopics.ownMacAddress, lambda data: handleMessage(result, data))
    uart._usbDev.requestMacAddress()

    counter = 0
    while result[0] and counter < 50:
        counter += 1
        time.sleep(0.05)

    UartEventBus.unsubscribe(subscriptionId)
    return result[1]


initLibs()

time.sleep(1)

enableUart()

time.sleep(1)

mac = _getMacAddress()

print("MACY", mac)
try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    uart.stop()