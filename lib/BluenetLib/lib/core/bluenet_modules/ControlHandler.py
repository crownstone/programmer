import time

from BluenetLib.Exceptions import BluenetException, BleError

from BluenetLib.lib.protocol.Characteristics import CrownstoneCharacteristics
from BluenetLib.lib.protocol.ControlPackets import ControlPacketsGenerator
from BluenetLib.lib.protocol.Services import CSServices
from BluenetLib.lib.util.EncryptionHandler import EncryptionHandler
from bluepy.btle import BTLEException

class ControlHandler:
    def __init__(self, bluetoothCore):
        self.core = bluetoothCore

    def getAndSetSessionNone(self):
        # read the nonce
        rawNonce = self.core.ble.readCharacteristicWithoutEncryption(CSServices.CrownstoneService, CrownstoneCharacteristics.SessionNonce)

        # decrypt it
        decryptedNonce = EncryptionHandler.decryptSessionNonce(rawNonce, self.core.settings.basicKey)

        # load into the settings object
        self.core.settings.setSessionNonce(decryptedNonce)


    def setSwitchState(self, switchState):
        """
         :param switchState: number [0..1]
        """
        self._writeControlPacket(ControlPacketsGenerator.getSwitchStatePacket(switchState))

    def switchRelay(self, switchState):
        """
         :param switchState: number 0 is off, 1 is on.
        """
        self._writeControlPacket(ControlPacketsGenerator.getRelaySwitchPacket(switchState))

    def switchPWM(self, switchState):
        """
         :param switchState: number [0..1]
        """
        self._writeControlPacket(ControlPacketsGenerator.getPwmSwitchPacket(switchState))

    def commandFactoryReset(self):
        """
          If you have the keys, you can use this to put the crownstone back into factory default mode
        """
        self._writeControlPacket(ControlPacketsGenerator.getCommandFactoryResetPacket())

    def allowDimming(self, allow):
        """
        :param allow: bool
        """
        self._writeControlPacket(ControlPacketsGenerator.getAllowDimmingPacket(allow))

    def disconnect(self):
        """
          This forces the Crownstone to disconnect from you
        """
        try:
            self._writeControlPacket(ControlPacketsGenerator.getDisconnectPacket())
            self.core.ble.disconnect()
        except BTLEException as err:
            if err.code is BTLEException.DISCONNECTED:
                pass
            else:
                raise err



    def lockSwitch(self, lock):
        """
        :param lock: bool
        """
        self._writeControlPacket(ControlPacketsGenerator.getLockSwitchPacket(lock))


    def reset(self):
        self._writeControlPacket(ControlPacketsGenerator.getResetPacket())



    def recovery(self, address):
        self.core.connect(address, ignoreEncryption=True)
        self._recoveryByFactoryReset()
        self._checkRecoveryProcess()
        self.core.disconnect()
        time.sleep(5)
        self.core.connect(address, ignoreEncryption=True)
        self._recoveryByFactoryReset()
        self._checkRecoveryProcess()
        self.core.disconnect()
        time.sleep(2)

    def _recoveryByFactoryReset(self):
        packet = ControlPacketsGenerator.getFactoryResetPacket()
        return self.core.ble.writeToCharacteristicWithoutEncryption(
            CSServices.CrownstoneService,
            CrownstoneCharacteristics.FactoryReset,
            packet
        )

    def _checkRecoveryProcess(self):
        result = self.core.ble.readCharacteristicWithoutEncryption(CSServices.CrownstoneService, CrownstoneCharacteristics.FactoryReset)
        if result[0] == 1:
            return True
        elif result[0] == 2:
            raise BluenetException(BleError.RECOVERY_MODE_DISABLED, "The recovery mechanism has been disabled by the Crownstone owner.")
        else:
            raise BluenetException(BleError.NOT_IN_RECOVERY_MODE, "The recovery mechanism has expired. It is only available briefly after the Crownstone is powered on.")


    #  self.bleManager.readCharacteristic(CSServices.CrownstoneService, characteristicId: CrownstoneCharacteristics.FactoryReset)
    # {(result:[UInt8]) -> Void in
    # if (result[0] == 1)
    #     seal.fulfill(())
    # else if (result[0] == 2) {
    # seal.reject(BluenetError.RECOVER_MODE_DISABLED)
    # else {
    # seal.reject(BluenetError.NOT_IN_RECOVERY_MODE)
    # .catch{(err) -> Void in
    # seal.reject(BluenetError.CANNOT_READ_FACTORY_RESET_CHARACTERISTIC)


    # return self.bleManager.connect(uuid)}
    # .then
    # {(_) -> Promise < Void > in
    # return self._recoverByFactoryReset()}
    # .then
    # {(_) -> Promise < Void > in
    # return self._checkRecoveryProcess()}
    # .then
    # {(_) -> Promise < Void > in
    # return self.bleManager.disconnect()}
    # .then
    # {(_) -> Promise < Void > in
    # return self.bleManager.waitToReconnect()}
    # .then
    # {(_) -> Promise < Void > in
    # return self.bleManager.connect(uuid)}
    # .then
    # {(_) -> Promise < Void > in
    # return self._recoverByFactoryReset()}
    # .then
    # {(_) -> Promise < Void > in
    # return self._checkRecoveryProcess()}
    # .then
    # {(_) -> Promise < Void > in
    # self.bleManager.settings.restoreEncryption()
    # return self.bleManager.disconnect()



    """
    ---------------  UTIL  ---------------
    """




    def _readControlPacket(self, packet):
        return self.core.ble.readCharacteristic(CSServices.CrownstoneService, CrownstoneCharacteristics.Control)

    def _writeControlPacket(self, packet):
        self.core.ble.writeToCharacteristic(CSServices.CrownstoneService, CrownstoneCharacteristics.Control, packet)
  