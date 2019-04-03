from util import path

import signal,time, asyncio, sys

# if this script is running, the button has been pressed

# check if the lid is closed

# flash Crownstone                                       --> ERROR 1

# UART --> Enable UART
# UART --> Ask for MAC address
# BLE --> Scan for setup signal from said MAC address
# BLE --> BLE fast setup --> THIS TURNS THE RELAY ON AUTOMATICALLY

# BLE--> Check for advertisements in normal mode
# UART --> Get power measurement for the 3W (HIGH REF)
# UART --> Turn relay off
# UART --> Get power measurement to check if 0W (ZERO REF) threshold ZERO to atleast 2W lower HIGH

# UART --> turn IGBTs on
# UART --> Get power measurement for the 3W (HIGH MATCH)
# UART --> turn IGBT off

# flash Crownstone again

from DisplayBoard.DisplayDriver import DisplayDriver
from DisplayBoard.LoadingRunner import LoadingRunner
from util.util import programCrownstone

from enum import Enum

from vendor.bluepy.btle import BTLEException


class ErrorCodes(Enum):
    E_NO_UART_RESTART_TEST           = [0]
    E_TESTER_NOT_WORKING             = [1]
    E_COULD_NOT_PROGRAM              = [2,1]
    E_COULD_NOT_PROGRAM_3v3_TOO_LOW  = [2,2]
    E_COULD_NOT_PROGRAM_NO_3V3       = [2,3]
    E_COULD_NOT_PROGRAM_JLINK_FAILED = [2,4]
    E_3V3_TOO_LOW                    = [3]
    E_NOT_SEEN_IN_SETUP_MODE         = [4]
    E_NO_BLE_SCAN_RECEIVED           = [5]
    E_COULD_NOT_SETUP                = [6]
    E_RELAY_NOT_ON                   = [7,1]
    E_RELAY_NOT_OFF                  = [7,2]
    E_RELAY_NOT_WORKING              = [7,3]
    E_POWER_MEASUREMENT_NOT_WORKING  = [8]
    E_CAN_NOT_TURN_ON_IGBTS          = [9,1]
    E_IGBT_Q1_NOT_WORKING            = [9,2,1]
    E_IGBT_Q2_NOT_WORKING            = [9,2,2]
    E_IGBTS_NOT_WORKING              = [9,2,3]


def gt():
    return "{:.3f}".format(time.time())


UART_ADDRESS = "/dev/ttyACM0"

class OverrideProgger:

    def __init__(self):
        self.loop = asyncio.new_event_loop()

        self.loadingRunner = None
        self.running = True
        self.macAddress = None
        self.highPowerMeasurement = 3
        self.lowPowerMeasurement = 0

        self.displayDriver = DisplayDriver()
        self.displayDriver.start()

        self.loadingRunner = LoadingRunner()

        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

        # run tests
        self.loop.run_until_complete(self.runTests())


    def close(self, source=None, frame=None):
        self.loadingRunner.stop()
        self.displayDriver.clearDisplay(True)
        self.displayDriver.cleanup()
        self.running = False
        time.sleep(2)
        quit()


    async def runTests(self):
        # show loading bar
        self.loadingRunner.start()

        print(gt(), "----- Programming the Crownstone...")
        initialProgrammingResult = programCrownstone()

        self.loadingRunner.setProgress( 3 / 6 )
        if initialProgrammingResult[0] == 0:
            if initialProgrammingResult[1] < 3.2:
                await self.endInErrorCode(ErrorCodes.E_3V3_TOO_LOW)
                return

            print(gt(), "----- Programming completed successfully!")
            await self.endInSuccess()
            return
        else:
            print("Failed to program, Result", initialProgrammingResult)
            # failed programming the Crownstone
            if initialProgrammingResult[1] is None:
                await self.endInErrorCode(ErrorCodes.E_COULD_NOT_PROGRAM_JLINK_FAILED)
            if initialProgrammingResult[1] < 3.2:
                await self.endInErrorCode(ErrorCodes.E_COULD_NOT_PROGRAM_3v3_TOO_LOW)
            else:
                await self.endInErrorCode(ErrorCodes.E_COULD_NOT_PROGRAM)



    async def endInErrorCode(self, code):
        print(gt(), "----- ----- ENDED IN ERROR CODE", code)
        codeArray = code.value
        self.loadingRunner.stop()
        while self.running:
            self.displayDriver.setSymbol("E")
            await self._quickSleeper(0.7)
            for errCode in codeArray:
                if self.running:
                    self.displayDriver.setSymbol(errCode)
                    await self._quickSleeper(0.7)
                    self.displayDriver.clearDisplay(True)
                    await self._quickSleeper(0.1)


    async def _quickSleeper(self, seconds):
        while seconds > 0 and self.running:
            await asyncio.sleep(0.1)
            seconds -= 0.1

    async def endInSuccess(self):
        self.loadingRunner.stop()

        await self.displayDriver.showBuildUp()
        while self.running:
            self.displayDriver.setSymbol('d')
            await self._quickSleeper(0.2)
            if self.running:
                self.displayDriver.clearDisplay(True)
                await self._quickSleeper(0.2)

if __name__ == "__main__":
    a = OverrideProgger()
