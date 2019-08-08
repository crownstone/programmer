import time

from BluenetLib.lib.packets.ResultPacket import ResultPacket
from BluenetLib.lib.protocol.ControlPackets import ControlPacketsGenerator

from BluenetLib.Exceptions import BleError, BluenetBleException
from BluenetLib.lib.protocol.BlePackets import WriteConfigPacket, ControlPacket
from BluenetLib.lib.protocol.BluenetTypes import ConfigurationType, ControlType, ProcessType, ResultValue
from BluenetLib.lib.protocol.Characteristics import SetupCharacteristics
from BluenetLib.lib.protocol.Services import CSServices
from BluenetLib.lib.util.Conversion import Conversion

from bluepy.btle import BTLEException


class SetupHandler:
    def __init__(self, bluetoothCore):
        self.core = bluetoothCore

    def hasCharacteristic(self, characteristics, uuid):
        for char in characteristics:
            if char.uuid == uuid:
                return True
        return False

    def setup(self, sphereId, crownstoneId, meshAccessAddress, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        characteristics = self.core.ble.getCharacteristics(CSServices.SetupService)

        if self.hasCharacteristic(characteristics, SetupCharacteristics.SetupControlV2):
            print("BluenetBLE: Fast Setup V2 is supported. Performing..")
            self.fastSetupV2(sphereId, crownstoneId, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor)
        elif self.hasCharacteristic(characteristics, SetupCharacteristics.SetupControl):
            print("BluenetBLE: Fast Setup is supported. Performing..")
            self.fastSetup(crownstoneId, meshAccessAddress, ibeaconUUID, ibeaconMajor, ibeaconMinor)
        else:
            print("BluenetBLE: Fast Setup is NOT supported. Performing classic setup..")
            self.classicSetup(crownstoneId, meshAccessAddress, ibeaconUUID, ibeaconMajor, ibeaconMinor)


    def fastSetupV2(self, sphereId, crownstoneId, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        if not self.core.settings.initializedKeys:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Keys are not initialized so I can't put anything on the Crownstone. Make sure you call .setSettings(adminKey, memberKey, basicKey, serviceDataKey, localizationKey, meshApplicationKey, meshNetworkKey")

        self.handleSetupPhaseEncryption()
        self.core.ble.setupNotificationStream(
            CSServices.SetupService,
            SetupCharacteristics.SetupControlV2,
            lambda: self._writeFastSetupV2(sphereId, crownstoneId, meshDeviceKey, ibeaconUUID, ibeaconMajor, ibeaconMinor),
            lambda notificationResult: self._handleResult(notificationResult),
            5
        )
        print("BluenetBLE: Closing Setup V2.")
        self.core.settings.exitSetup()


    def fastSetup(self, crownstoneId, meshAccessAddress, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        if not self.core.settings.initializedKeys:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Keys are not initialized so I can't put anything on the Crownstone. Make sure you call .setSettings(adminKey, memberKey, basicKey, serviceDataKey, localizationKey, meshApplicationKey, meshNetworkKey")

        self.handleSetupPhaseEncryption()
        self.core.ble.setupNotificationStream(
            CSServices.SetupService,
            SetupCharacteristics.SetupControl,
            lambda: self._writeFastSetup(crownstoneId, meshAccessAddress, ibeaconUUID, ibeaconMajor, ibeaconMinor),
            lambda notificationResult: self._handleResult(notificationResult),
            5
        )
        print("BluenetBLE: Closing Setup.")
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
        self.core.ble.writeToCharacteristic(CSServices.SetupService, SetupCharacteristics.SetupControlV2, packet)

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
            payload = response.getUInt16Payload()
            if payload == ResultValue.WAIT_FOR_SUCCESS:
                print("BluenetBLE: Waiting for setup data to be stored on Crownstone...")
                return ProcessType.CONTINUE
            elif payload == ResultValue.SUCCESS:
                print("BluenetBLE: Data stored...")
                return ProcessType.FINISHED
            else:
                print("BluenetBLE: Unexpected notification data. Aborting...")
                return ProcessType.ABORT_ERROR
        else:
            print("BluenetBLE: Invalid notification data. Aborting...")
            return ProcessType.ABORT_ERROR
        

    def classicSetup(self, crownstoneId, meshAccessAddress, ibeaconUUID, ibeaconMajor, ibeaconMinor):
        if not self.core.settings.initializedKeys:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Keys are not initialized so I can't put anything on the Crownstone. Make sure you call .setSettings(True, adminKey, memberKey, guesKey")
        
        sleepTime = 0.4
        
        print("BluenetBLE: Starting Setup...")
        print("BluenetBLE: Setting up encryption...")
        self.handleSetupPhaseEncryption()
        
        try:
            print("BluenetBLE: Setting Admin Key...")
            self.writeAdminKey(self.core.settings.adminKey)
            time.sleep(sleepTime)
            print("BluenetBLE: Setting Member Key...")
            self.writeMemberKey(self.core.settings.memberKey)
            time.sleep(sleepTime)
            print("BluenetBLE: Setting Basic Key...")
            self.writeBasicKey(self.core.settings.basicKey)
            time.sleep(sleepTime)
            print("BluenetBLE: Setting Crownstone ID...")
            self.writeCrownstoneId(crownstoneId)
            time.sleep(sleepTime)
            print("BluenetBLE: Setting Mesh Access Address...")
            self.writeMeshAccessAddress(meshAccessAddress)
            time.sleep(sleepTime)
            print("BluenetBLE: Setting iBeacon UUID...")
            self.writeIBeaconUUID(ibeaconUUID)
            time.sleep(sleepTime)
            print("BluenetBLE: Setting iBeacon Major...")
            self.writeIBeaconMajor(ibeaconMajor)
            time.sleep(sleepTime)
            print("BluenetBLE: Setting iBeacon Minor...")
            self.writeIBeaconMinor(ibeaconMinor)
            time.sleep(sleepTime)
            print("BluenetBLE: Wrapping up...")
            self.validateSetup()
            time.sleep(2*sleepTime)
            print("BluenetBLE: Setup complete!")
        except BTLEException as err:
            raise err
        except BluenetBleException as err:
            raise err
        finally:
            self.core.settings.exitSetup()
        
        
    def handleSetupPhaseEncryption(self):
        sessionKey   = self.core.ble.readCharacteristicWithoutEncryption(CSServices.SetupService, SetupCharacteristics.SessionKey)
        sessionNonce = self.core.ble.readCharacteristicWithoutEncryption(CSServices.SetupService, SetupCharacteristics.SessionNonce)
        
        self.core.settings.loadSetupKey(sessionKey)
        self.core.settings.setSessionNonce(sessionNonce)
        
    
    def writeCrownstoneId(self, crownstoneId):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.CROWNSTONE_IDENTIFIER)
                .loadUInt16(crownstoneId)
                .getPacket())

    def writeAdminKey(self, adminKey):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.ADMIN_ENCRYPTION_KEY)
                .loadByteArray(adminKey)
                .getPacket())

    def writeMemberKey(self, memberKey):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.MEMBER_ENCRYPTION_KEY)
                .loadByteArray(memberKey)
                .getPacket())

    def writeBasicKey(self, basicKey):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.BASIC_ENCRYPTION_KEY)
                .loadByteArray(basicKey)
                .getPacket())

    def writeMeshAccessAddress(self, meshAccessAddress):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.MESH_ACCESS_ADDRESS)
                .loadByteArray(Conversion.hex_string_to_uint8_array(meshAccessAddress))
                .getPacket())

    def writeIBeaconUUID(self, ibeaconUUID):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.IBEACON_UUID)
                .loadByteArray(Conversion.ibeaconUUIDString_to_reversed_uint8_array(ibeaconUUID))
                .getPacket())

    def writeIBeaconMajor(self, ibeaconMajor):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.IBEACON_MAJOR)
                .loadUInt16(ibeaconMajor)
                .getPacket())

    def writeIBeaconMinor(self, ibeaconMinor):
        self._writeConfigPacket(
            WriteConfigPacket(ConfigurationType.IBEACON_MINOR)
                .loadUInt16(ibeaconMinor)
                .getPacket())

    def validateSetup(self):
        self.core.ble.writeToCharacteristic(CSServices.SetupService, SetupCharacteristics.Control, ControlPacket(ControlType.VALIDATE_SETUP).getPacket())
    
    
    def _writeConfigPacket(self, packet):
        self.core.ble.writeToCharacteristic(CSServices.SetupService, SetupCharacteristics.ConfigControl, packet)
        
        returnCode = self.core.ble.readCharacteristic(CSServices.SetupService, SetupCharacteristics.ConfigControl)
        
        if returnCode[0] != 0:
            raise BluenetBleException(BleError.RETURN_CODE_NOT_SUCCESSFUL, "The Crownstone returned a different code than 0 as a response to the config control write: " + str(returnCode[0]))
        
        