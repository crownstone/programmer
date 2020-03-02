from getPinLayout import ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING, REQUIRED_RSSI
from util import path

import signal,time, asyncio, sys, random

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

from BluenetLib import Bluenet, BluenetEventBus, UsbTopics, Util, BluenetBleException
from BluenetLib.BLE import BluenetBle
from BluenetLib.lib.topics.DevTopics import DevTopics
from DisplayBoard.DisplayDriver import DisplayDriver
from DisplayBoard.LoadingRunner import LoadingRunner
from lib.PowerStateMeasurement.PowerStateMeasurement import PowerStateMeasurement
from util.util import programCrownstone, findUsbBleDongleHciIndex, findUartAddress

from enum import Enum

from vendor.bluepy.btle import BTLEException

IGBTs = 1
RELAY = 2

TESTING_CROWNSTONE_ID = random.randint(1,250)

class ErrorCodes(Enum):
    E_NO_UART_RESTART_TEST           = [0]
    E_COULD_NOT_FIND_CROWNSTONE      = [1,1]
    E_TESTER_NOT_WORKING             = [1,2]
    E_COULD_NOT_PROGRAM              = [2,1]
    E_COULD_NOT_PROGRAM_3v3_TOO_LOW  = [2,2]
    E_COULD_NOT_PROGRAM_JLINK_FAILED = [2,3]
    E_3V3_TOO_LOW                    = [2,4]
    E_THERMAL_FUSE_BUST              = [3]
    E_NO_BLE_SCAN_RECEIVED           = [4,1]
    E_NOT_SEEN_IN_SETUP_MODE         = [4,2]
    E_RSSI_TOO_LOW                   = [5]
    E_COULD_NOT_SETUP                = [6]
    E_RELAY_NOT_ON                   = [7,1]
    E_RELAY_NOT_OFF                  = [7,2]
    E_POWER_MEASUREMENT_NOT_WORKING  = [8]
    E_IGBT_Q1_NOT_WORKING            = [9,1]
    E_IGBT_Q2_NOT_WORKING            = [9,2]
    E_IGBTS_NOT_WORKING              = [9,3]
    E_CAN_NOT_TURN_ON_IGBTS          = [9,4]


def gt():
    return "{:.3f}".format(time.time())


class TestRunner:

    def __init__(self):
        self.loop = asyncio.new_event_loop()

        self.bluenet = None
        self.bluenetBLE = None
        self.loadingRunner = None
        self.running = True
        self.macAddress = None
        self.highPowerMeasurement = 3
        self.lowPowerMeasurement = 0

        self.displayDriver = DisplayDriver()
        self.displayDriver.start()

        self.powerState = PowerStateMeasurement()
        self.powerState.setup()

        self.loadingRunner = LoadingRunner()

        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

        # run tests
        self.loop.run_until_complete(self.runTests())




    def close(self, source=None, frame=None):
        print(gt(), "----- Closing Test...")
        self.cleanup()
        self.loadingRunner.stop()
        try:
            self.displayDriver.clearDisplay(True)
        except:
            print(gt(), "----- Error while cleaning display")

        self.displayDriver.cleanup()
        self.powerState.cleanup()
        self.running = False
        print(gt(), "----- Test is closed. Quitting Test...")
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

        print(gt(), "----- Programming the Crownstone...")
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

            if await self.getRssiAverage(REQUIRED_RSSI) is False:
                return

            await self.setupCrownstone()

            self.loadingRunner.setProgress(3 / 6)

            if await self.checkForNormalMode() is False:
                return

            if await self.getRssiAverage(REQUIRED_RSSI) is False:
                return

            # power cycle relay
            print(gt(), "----- Power cycle relay to avoid power measurement bug.")
            self.relayOff()
            await self._quickSleeper(2)
            self.relayOn()

            if await self.checkIfLoadIsPowered(RELAY) is False:
                return
            if await self.checkHighPowerState() is False:
                return

            self.loadingRunner.setProgress(4 / 6)

            # extra await to ensure the IGBT driver is charged.
            await self._quickSleeper(2)

            self.relayOff()
            if await self.checkIfLoadIsNotPowered() is False:
                return
            if await self.checkLowPowerState() is False:
                return

            # extra await to ensure the firmware decides that the dimmer can be used.

            print(gt(), "----- Waiting for dimmer circuit to power up...0%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up... 12.5%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up... 25%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up... 37.5%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up....50%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up... 62.5%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up... 75%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up... 87.5%")
            await self._quickSleeper(ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING / 8)
            print(gt(), "----- Waiting for dimmer circuit to power up... 100%")
            print(gt(), "----- Turn on the IGBTs")

            if await self.igbtsOn() is False:
                return
            if await self.checkIfLoadIsPowered(IGBTs) is False:
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
                print(gt(), "----- Could not reprogram Crownstone")
                if secondProgrammingResult[1] < 3.2:
                    await self.endInErrorCode(ErrorCodes.E_3V3_TOO_LOW)
                    return
                await self.endInErrorCode(ErrorCodes.E_COULD_NOT_PROGRAM)
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



    async def initLibs(self):
        import traceback
        self.bluenet = Bluenet()
        try:
            address = findUartAddress()
            if address == False:
                await self.endInErrorCode(ErrorCodes.E_COULD_NOT_FIND_CROWNSTONE)
                return False
            else:
                self.bluenet.initializeUSB(address)
        except:
            print(gt(), "----- ----- Error in settings UART Address", sys.exc_info()[0])
            traceback.print_exc()
            await self.endInErrorCode(ErrorCodes.E_TESTER_NOT_WORKING)
            return False

        print(gt(), "----- Initializing Bluenet Libraries")
        self.bluenetBLE = BluenetBle(hciIndex=findUsbBleDongleHciIndex())
        self.bluenetBLE.setSettings(
            adminKey=           "adminKeyForCrown",
            memberKey=          "memberKeyForHome",
            basicKey=           "guestKeyForOther",
            serviceDataKey=     "guestKeyForOther",
            localizationKey=    "localizationKeyX",
            meshApplicationKey= "meshKeyForStones",
            meshNetworkKey=     "meshAppForStones",
        )


    async def enableUart(self):
        # enable UART
        print(gt(), "----- Enabling UART...")
        self.bluenet._usbDev.setUartMode(3)
        await self._quickSleeper(0.75)


    async def getRssiAverage(self, threshold):
        # kill test here if we need to stop.TestRunner.py
        if not self.running:
            return False

        print(gt(), "----- Checking Crownstone RSSI...")
        # BLE--> Check for advertisements in normal mode
        average = self.bluenetBLE.getRssiAverage(self.macAddress, scanDuration=4)
        if average is None:
            print(gt(), "----- Checking Crownstone RSSI... (again)")
            average = self.bluenetBLE.getRssiAverage(self.macAddress, scanDuration=4)
            if average is None:
                await self.endInErrorCode(ErrorCodes.E_NO_BLE_SCAN_RECEIVED)
                return False

        print(gt(), "----- Crownstone RSSI is ", average, " with threshold", threshold)
        if average < threshold:
            await self.endInErrorCode(ErrorCodes.E_RSSI_TOO_LOW)
            return False

    async def getMacAddress(self):
        # UART --> Ask for MAC address
        print(gt(), "----- Get MAC address...")
        self.macAddress = await self._getMacAddress()
        print(gt(), "----- Received MAC address:", self.macAddress)
        if self.macAddress is None:
            await self.endInErrorCode(ErrorCodes.E_NO_UART_RESTART_TEST)
            return False


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
        # kill test here if we need to stop.TestRunner.py
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

        print(gt(), "----- Setup was successful. Crownstone is in normal mode")


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
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False
        elif measurement["powerMeasurement"] < (self.highPowerMeasurement - 1):
            self.lowPowerMeasurement = measurement["powerMeasurement"]
            pass
        else:
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False


    def relayOn(self):
        # UART --> Turn relay off
        print(gt(), "----- Turn RELAY ON...")
        self.bluenet._usbDev.toggleRelay(True)


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


    async def checkIfLoadIsPowered(self, type):
        await asyncio.sleep(0.5)
        self.powerState.checkPowerStates(2)
        if not self.powerState.powerThroughLoad():

            # no power through the load
            # on the upside, IGBTs are not leaking!
            if type == IGBTs:
                await self.endInErrorCode(ErrorCodes.E_IGBTS_NOT_WORKING)
            else:
                await self.endInErrorCode(ErrorCodes.E_THERMAL_FUSE_BUST)
            return False
        elif not self.powerState.powerThroughI1():
            # no power though I1 (Q1)
            # this IGBT is broken
            await self.endInErrorCode(ErrorCodes.E_IGBT_Q1_NOT_WORKING)
            return False
        elif not self.powerState.powerThroughI2():
            # no power though I2 (Q2)
            # this IGBT is broken
            await self.endInErrorCode(ErrorCodes.E_IGBT_Q2_NOT_WORKING)
            return False
        else:
            return True



    async def checkIfLoadIsNotPowered(self):
        await asyncio.sleep(0.5)
        self.powerState.checkPowerStates(0.5)
        if self.powerState.powerThroughI1() and self.powerState.powerThroughI2():
            # power through the load, Q1 and Q2 are leaking (or RELAY wont turn off)
            await self.endInErrorCode(ErrorCodes.E_IGBTS_NOT_WORKING)
            return False
        elif self.powerState.powerThroughI1():
            # no power though I1 (Q1)
            # this IGBT is broken
            await self.endInErrorCode(ErrorCodes.E_IGBT_Q1_NOT_WORKING)
            return False
        elif self.powerState.powerThroughI2():
            # no power though I2 (Q2)
            # this IGBT is broken
            await self.endInErrorCode(ErrorCodes.E_IGBT_Q2_NOT_WORKING)
            return False
        else:
            return True


    async def verifyHighPowerState(self, attempt=0):
        # kill test here if we need to stop.
        if not self.running:
            return False

        print(gt(), "----- Getting measurement for IGBT's ON... attempt number ", attempt)
        measurement = await self.getPowerMeasurement(100)

        if measurement["powerMeasurement"] is None:
            await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
            return False
        elif measurement["switchState"] != 100:
            await self.endInErrorCode(ErrorCodes.E_CAN_NOT_TURN_ON_IGBTS)
            return False
        else:
            dW_measure_high = abs(measurement["powerMeasurement"] - self.highPowerMeasurement)
            dW_measure_low = abs(measurement["powerMeasurement"] - self.lowPowerMeasurement)
            print("dW_measure_high > dW_measure_low", dW_measure_high, dW_measure_low)
            if dW_measure_high < dW_measure_low:
                pass
            elif dW_measure_high > dW_measure_low and attempt > 2:
                await self.endInErrorCode(ErrorCodes.E_IGBTS_NOT_WORKING)
                return False
            elif attempt > 2:
                await self.endInErrorCode(ErrorCodes.E_POWER_MEASUREMENT_NOT_WORKING)
                return False
            else:
                print("Received measurement", measurement["powerMeasurement"], "vs high", self.highPowerMeasurement, "vs low", self.lowPowerMeasurement)
                return await self.verifyHighPowerState(attempt+1)


    async def setupCrownstone(self):
        print(gt(), "----- Setting up Crownstone...")
        try:
            # BLE --> BLE fast setup --> THIS TURNS THE RELAY ON AUTOMATICALLY
            self.bluenetBLE.setupCrownstone(
                self.macAddress,
                sphereId=1,
                crownstoneId=TESTING_CROWNSTONE_ID,
                meshAccessAddress=Util.generateMeshAccessAddress(),
                meshDeviceKey="itsMyDeviceKeyyy",
                ibeaconUUID="1843423e-e175-4af0-a2e4-31e32f729a8a",
                ibeaconMajor=123,
                ibeaconMinor=456
            )
        except:
            err = sys.exc_info()[0]
            if type(sys.exc_info()[0]) is BTLEException:
                print(gt(), "----- Crownstone might have failed to setup... BTLE", err.message, err.__str__())
            elif type(sys.exc_info()[0]) is BluenetBleException:
                print(gt(), "----- Crownstone might have failed to setup... BTLE", err.message, err.type, err.code)
            else:
                print(gt(), "----- Crownstone might have failed to setup... checking...", err)



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
            if data["id"] == TESTING_CROWNSTONE_ID:
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
