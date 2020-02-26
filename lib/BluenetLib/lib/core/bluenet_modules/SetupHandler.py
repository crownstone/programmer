from BluenetLib.lib.packets.ResultPacket import ResultPacket
from BluenetLib.lib.protocol.ControlPackets import ControlPacketsGenerator
from BluenetLib.Exceptions import BleError, BluenetBleException
from BluenetLib.lib.protocol.BluenetTypes import ControlType, ResultValue, ProcessType
from BluenetLib.lib.protocol.Characteristics import SetupCharacteristics
from BluenetLib.lib.protocol.Services import CSServices

class SetupHandler:
    def __init__(self, bluetoothCore):
        self.core = bluetoothCore

    def setup(self, address, sphereId, crownstoneId, meshAccessAddress, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        characteristics = self.core.ble.getCharacteristics(CSServices.SetupService)
        try:
            self.fastSetupV2(sphereId, crownstoneId, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor)
        except BluenetBleException as e:
            if e.type is not BleError.NOTIFICATION_STREAM_TIMEOUT:
                raise e
        isNormalMode = self.core.isCrownstoneInNormalMode(address, 10, waitUntilInRequiredMode=True)
        if not isNormalMode:
            raise BluenetBleException(BleError.SETUP_FAILED, "The setup has failed.")


    def fastSetupV2(self, sphereId, crownstoneId, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        if not self.core.settings.initializedKeys:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Keys are not initialized so I can't put anything on the Crownstone. Make sure you call .setSettings(adminKey, memberKey, basicKey, serviceDataKey, localizationKey, meshApplicationKey, meshNetworkKey")

        self.handleSetupPhaseEncryption()
        self.core.ble.setupNotificationStream(
            CSServices.SetupService,
            SetupCharacteristics.SetupControl,
            lambda: self._writeFastSetupV2(sphereId, crownstoneId, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor),
            lambda notificationResult: self._handleResult(notificationResult),
            3
        )

        print("BluenetBLE: Closing Setup V2.")
        self.core.settings.exitSetup()


    def _writeFastSetupV2(self, sphereId, crownstoneId, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        packet = ControlPacketsGenerator.getSetupPacketV2(
            crownstoneId,
            sphereId,
            self.core.settings.adminKey,
            self.core.settings.memberKey,
            self.core.settings.basicKey,
            self.core.settings.serviceDataKey,
            self.core.settings.localizationKey,
            meshDeviceKey,
            self.core.settings.meshApplicationKey,
            self.core.settings.meshNetworkKey,
            ibeaconUUID,
            ibeaconMajor,
            ibeaconMinor
        )

        print("BluenetBLE: Writing setup data to Crownstone...")
        self.core.ble.writeToCharacteristic(CSServices.SetupService, SetupCharacteristics.SetupControl, packet)

    def _writeFastSetup(self, crownstoneId, meshAccessAddress, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        packet = ControlPacketsGenerator.getSetupPacket(
            0,
            crownstoneId,
            self.core.settings.adminKey,
            self.core.settings.memberKey,
            self.core.settings.basicKey,
            meshAccessAddress,
            ibeaconUUID,
            ibeaconMajor,
            ibeaconMinor
        )

        print("BluenetBLE: Writing setup data to Crownstone...")
        self.core.ble.writeToCharacteristic(CSServices.SetupService, SetupCharacteristics.SetupControl, packet)


    def _handleResult(self, result):
        response = ResultPacket(result)
        if response.valid:
            if response.resultCode == ResultValue.WAIT_FOR_SUCCESS:
                print("BluenetBLE: Waiting for setup data to be stored on Crownstone...")
                return ProcessType.CONTINUE
            elif response.resultCode == ResultValue.SUCCESS:
                print("BluenetBLE: Data stored...")
                return ProcessType.FINISHED
            else:
                print("BluenetBLE: Unexpected notification data. Aborting...")
                return ProcessType.ABORT_ERROR
        else:
            print("BluenetBLE: Invalid notification data. Aborting...")
            return ProcessType.ABORT_ERROR


    def handleSetupPhaseEncryption(self):
        sessionKey   = self.core.ble.readCharacteristicWithoutEncryption(CSServices.SetupService, SetupCharacteristics.SessionKey)
        sessionNonce = self.core.ble.readCharacteristicWithoutEncryption(CSServices.SetupService, SetupCharacteristics.SessionNonce)
        
        self.core.settings.loadSetupKey(sessionKey)
        self.core.settings.setSessionNonce(sessionNonce)
