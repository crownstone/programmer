import signal,time, asyncio, sys
from util import path
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

from BluenetLib import Bluenet, BluenetEventBus, UsbTopics, Util
from BluenetLib.BLE import BluenetBle
from BluenetLib.lib.topics.DevTopics import DevTopics
from DisplayBoard.DisplayDriver import DisplayDriver
from DisplayBoard.LoadingRunner import LoadingRunner
from util.util import programCrownstone, findUsbBleDongleHciIndex

from enum import Enum

from vendor.bluepy.btle import BTLEException


class ErrorCodes(Enum):
    E_TESTER_NOT_WORKING            = [1]
    E_COULD_NOT_PROGRAM             = [2]
    E_3V3_TOO_LOW                   = [3]
    E_NO_MAC_ADDRESS                = [4,1]
    E_NOT_SEEN_IN_SETUP_MODE        = [4,2]
    E_NO_BLE_SCAN_RECEIVED          = [5]
    E_COULD_NOT_SETUP               = [6]
    E_RELAY_NOT_ON                  = [7,1]
    E_RELAY_NOT_OFF                 = [7,2]
    E_RELAY_NOT_WORKING             = [7,3]
    E_POWER_MEASUREMENT_NOT_WORKING = [8]
    E_CAN_NOT_TURN_ON_IGBTS         = [9,1]
    E_IGBTS_NOT_WORKING             = [9,2]


def gt():
    return "{:.3f}".format(time.time())


class TestRunner:

    def __init__(self):
        self.displayDriver = DisplayDriver()
        self.displayDriver.start()

        self.loadingRunner = LoadingRunner()

        self.macAddress = None
        self.highPowerMeasurement = 3
        self.lowPowerMeasurement = 0

        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

        self.loop = asyncio.new_event_loop()

        # run tests
        self.loop.run_until_complete(self.runTests())

        self.bluenet = None
        self.bluenetBLE = None
        self.loadingRunner = None
        self.running = True


    def close(self, source=None, frame=None):
        self.cleanup()
        self.loadingRunner.stop()
        self.displayDriver.clearDisplay(True)
        self.displayDriver.cleanup()
        self.running = False
        time.sleep(2)
        quit()


    def cleanup(self):
        if self.bluenet is not None:
            self.bluenet.stop()

        if self.bluenetBLE is not None:
            self.bluenetBLE.shutDown()


    async def runTests(self):
        # show loading bar
        self.loadingRunner.start()

        print(gt(), "----- Programming Crownstone...")
        initialProgrammingResult = programCrownstone()
        self.loadingRunner.setProgress( 1 / 6 )
        if initialProgrammingResult[0] == 0:
            if initialProgrammingResult[1] < 3.2:
                await self.endInErrorCode(ErrorCodes.E_3V3_TOO_LOW)
                return

            if await self.initLibs() is False:
               return

            await self._quickSleeper(1.5)  # wait for reboot
            await self.enableUart()

            self.loadingRunner.setProgress(2 / 6)

            if await self.getMacAddress() is False: # will retry 2 times
                return
            if await self.checkForSetupMode() is False:
                return
            if await self.setupCrownstone() is False: # will retry 3 times
                return

            self.loadingRunner.setProgress(3 / 6)

            if await self.checkForNormalMode() is False:
                return
            if await self.checkHighPowerState() is False:
                return

            self.loadingRunner.setProgress(4 / 6)

            self.relayOff()
            if await self.checkLowPowerState() is False:
                return
            if await self.igbtsOn() is False:
                return
            if await self.verifyHighPowerState() is False:
                return


            self.loadingRunner.setProgress(5 / 6)

            # kill test here if we need to stop.
            if not self.running:
                return

            # flash Crownstone again
            print(gt(), "----- Test Complete, reprogramming Crownstone...")
            secondProgrammingResult = programCrownstone()
            if secondProgrammingResult[0] == 0:
                print(gt(), "----- Test completed successfully!")
                await self.endInSuccess()
                return
            else:
                print("Could not reprogram Crownstone")
                if secondProgrammingResult[1] < 3.2:
                    await self.endInErrorCode(ErrorCodes.E_3V3_TOO_LOW)
                    return
                await self.endInErrorCode(ErrorCodes.E_COULD_NOT_PROGRAM)
                return

        else:
            # failed programming the Crownstone
            await self.endInErrorCode(ErrorCodes.E_COULD_NOT_PROGRAM)
            return




    async def initLibs(self):
        # success
        self.bluenet = Bluenet()
        try:
            self.bluenet.initializeUSB("/dev/ttyACM0")  # TODO: get tty address dynamically
        except:
            print(gt(), "----- ----- Error in settings UART Address", sys.exc_info()[0])
            await self.endInErrorCode(ErrorCodes.E_TESTER_NOT_WORKING)
            return False

        print(gt(), "----- Initializing Bluenet Libraries")
        self.bluenetBLE = BluenetBle(hciIndex=findUsbBleDongleHciIndex())
        self.bluenetBLE.setSettings("adminKeyForCrown", "memberKeyForHome", "guestKeyForOther")


    async def enableUart(self):
        # enable UART
        print(gt(), "----- Enabling UART...")
        self.bluenet._usbDev.setUartMode(3)
        await self._quickSleeper(0.75)


    async def getMacAddress(self, attempt=0):
        # UART --> Ask for MAC address
        print(gt(), "----- Get MAC address...")
        self.macAddress = await self._getMacAddress()
        if self.macAddress is None:
            if attempt < 2:
                await self._quickSleeper(1)
                await self.getMacAddress(attempt+1)
            else:
                await self.endInErrorCode(ErrorCodes.E_NO_MAC_ADDRESS)
                return False
        print(gt(), "----- Received MAC address:", self.macAddress)


    async def checkForSetupMode(self):
        # kill test here if we need to stop.
        if not self.running:
            return False

        # BLE --> Scan for setup signal from said MAC address
        print(gt(), "----- Check if Crownstone is in setup Mode...")
        inSetupMode = self.bluenetBLE.isCrownstoneInSetupMode(self.macAddress)
        if inSetupMode is None:
            await self.endInErrorCode(ErrorCodes.E_NO_BLE_SCAN_RECEIVED)
            return False
        elif not inSetupMode:
            await self.endInErrorCode(ErrorCodes.E_NOT_SEEN_IN_SETUP_MODE)
            return False


    async def checkForNormalMode(self):
        # kill test here if we need to stop.
        if not self.running:
            return False

        print(gt(), "----- Checking if Crownstone is in normal mode...")
        # BLE--> Check for advertisements in normal mode
        isInNormalMode = self.bluenetBLE.isCrownstoneInNormalMode(self.macAddress, scanDuration=5, waitUntilInRequiredMode=True)
        if isInNormalMode is None:
            await self.endInErrorCode(ErrorCodes.E_NO_BLE_SCAN_RECEIVED)
            return False
        elif not isInNormalMode:
            await self.endInErrorCode(ErrorCodes.E_COULD_NOT_SETUP)
            return False


    async def checkHighPowerState(self):
        # kill test here if we need to stop.
        if not self.running:
            return False

        print(gt(), "----- Getting measurement for RELAY ON...")
        # UART --> Get power measurement for the 3W (HIGH REF)
        measurement = await self.getPowerMeasurement(128)
        if measurement["powerMeasurement"] is None:
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False
        elif measurement["switchState"] != 128:
            await self.endInErrorCode(ErrorCodes.E_RELAY_NOT_ON)
            return False
        else:
            self.highPowerMeasurement = measurement["powerMeasurement"]


    async def checkLowPowerState(self):
        # kill test here if we need to stop.
        if not self.running:
            return False

        # UART --> Get power measurement to check if 0W (ZERO REF) threshold ZERO to atleast 2W lower HIGH
        print(gt(), "----- Getting measurement for RELAY OFF...")
        measurement = await self.getPowerMeasurement(0)
        if measurement["powerMeasurement"] is None:
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False
        elif measurement["switchState"] != 0:
            await self.endInErrorCode(ErrorCodes.E_RELAY_NOT_OFF)
            return
        elif -1 < measurement["powerMeasurement"] - self.highPowerMeasurement < 1:
            await self.endInErrorCode(ErrorCodes.E_RELAY_NOT_WORKING)
            return False
        elif measurement["powerMeasurement"] < (self.highPowerMeasurement - 1):
            self.lowPowerMeasurement = measurement["powerMeasurement"]
            pass
        else:
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False


    def relayOff(self):
        # UART --> Turn relay off
        print(gt(), "----- Turn RELAY OFF...")
        self.bluenet._usbDev.toggleRelay(False)


    async def igbtsOn(self):
        # kill test here if we need to stop.
        if not self.running:
            return False

        # UART --> turn IGBTs on
        print(gt(), "----- Enabling Allow Dimming...")
        self.bluenet._usbDev.toggleAllowDimming(True)
        await self._quickSleeper(0.75)  # wait on write to CS storage of this new settings

        print(gt(), "----- Turning IGBT's ON...")
        self.bluenet._usbDev.toggleIGBTs(True)



    async def verifyHighPowerState(self):
        # kill test here if we need to stop.
        if not self.running:
            return False

        # UART --> Get power measurement for the 3W (HIGH MATCH)
        print(gt(), "----- Getting measurement for IGBT's ON...")
        measurement = await self.getPowerMeasurement(100)
        if measurement["powerMeasurement"] is None:
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False
        elif measurement["switchState"] != 100:
            await self.endInErrorCode(ErrorCodes.E_CAN_NOT_TURN_ON_IGBTS)
            return False
        elif -1 < measurement["powerMeasurement"] - self.highPowerMeasurement < 1:
            pass
        elif -1 < measurement["powerMeasurement"] - self.lowPowerMeasurement < 1:
            await self.endInErrorCode(ErrorCodes.E_IGBTS_NOT_WORKING)
            return False
        else:
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False


    async def setupCrownstone(self, attempt=0):
        if attempt > 3:
            return False

        print(gt(), "----- Setting up Crownstone... attempt #", attempt)
        try:
            # BLE --> BLE fast setup --> THIS TURNS THE RELAY ON AUTOMATICALLY
            self.bluenetBLE.setupCrownstone(
                self.macAddress,
                crownstoneId=1,
                meshAccessAddress=Util.generateMeshAccessAddress(),
                ibeaconUUID="1843423e-e175-4af0-a2e4-31e32f729a8a",
                ibeaconMajor=123,
                ibeaconMinor=456
            )
        except:
            err = sys.exc_info()[0]
            if type(sys.exc_info()[0]) is BTLEException:
                print("----- Crownstone might have failed to setup... BTLE", err.message, err.__str__())
            else:
                print("----- Crownstone might have failed to setup...", err)
            if self.running:
                await self._quickSleeper(1 + attempt)
                print("Retrying...")
                await self.setupCrownstone(self.macAddress, attempt + 1)


    async def _getMacAddress(self):
        result = [True, None]
        def handleMessage(container, data):
            container[0] = False
            container[1] = data

        subscriptionId = BluenetEventBus.subscribe(DevTopics.ownMacAddress, lambda data: handleMessage(result, data))
        self.bluenet._usbDev.requestMacAddress()

        counter = 0
        while result[0] and counter < 50:
            counter += 1
            await asyncio.sleep(0.05)

        BluenetEventBus.unsubscribe(subscriptionId)
        return result[1]


    async def getPowerMeasurement(self, expectedSwitchState):
        result = [True, None, None]
        def handleMessage(container, data):
            # check to ensure its this crownstone, not a mesh stone if there are multiple proggers
            if data["id"] == 1:
                # container[1] = (data["powerUsageReal"],data["powerUsageApparent"],data["powerFactor"])
                container[1] = data["powerUsageReal"]
                container[2] = data["switchState"]
                if data["switchState"] == expectedSwitchState:
                    # this will stop the measurement
                    container[0] = False

        subscriptionId = BluenetEventBus.subscribe(DevTopics.newServiceData, lambda data: handleMessage(result, data))

        counter = 0
        while result[0] and counter < 100:
            counter += 1
            await asyncio.sleep(0.05)

        if counter >= 100:
            print(gt(), "----- Get Power Measurement: Timeout Expired")

        BluenetEventBus.unsubscribe(subscriptionId)
        print(gt(), "----- Result in power measurement", result[1], "with switchState", result[2])
        return {"powerMeasurement":result[1], "switchState": result[2]}



    async def endInErrorCode(self, code):
        print(gt(), "----- ----- ENDED IN ERROR CODE", code)
        codeArray = code.value
        self.loadingRunner.stop()
        self.cleanup()
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
        self.cleanup()

        await self.displayDriver.showBuildUp()
        while self.running:
            self.displayDriver.setSymbol('d')
            await self._quickSleeper(0.2)
            if self.running:
                self.displayDriver.clearDisplay(True)
                await self._quickSleeper(0.2)

if __name__ == "__main__":
    a = TestRunner()
