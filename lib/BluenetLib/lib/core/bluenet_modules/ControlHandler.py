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
        decryptedNonce = EncryptionHandler.decryptSessionNonce(rawNonce, self.core.settings.guestKey)
        
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
    






    """
    ---------------  UTIL  ---------------
    """
    



    def _readControlPacket(self, packet):
        return self.core.ble.readCharacteristic(CSServices.CrownstoneService, CrownstoneCharacteristics.Control)

    def _writeControlPacket(self, packet):
        self.core.ble.writeToCharacteristic(CSServices.CrownstoneService, CrownstoneCharacteristics.Control, packet)
  