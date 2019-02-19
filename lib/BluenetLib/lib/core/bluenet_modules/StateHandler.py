from BluenetLib.lib.protocol.BlePackets import ReadStatePacket
from BluenetLib.lib.protocol.BluenetTypes import StateType
from BluenetLib.lib.protocol.Characteristics import CrownstoneCharacteristics
from BluenetLib.lib.protocol.Services import CSServices
from BluenetLib.lib.util.Conversion import Conversion


class StateHandler:
    def __init__(self, bluetoothCore):
        self.core = bluetoothCore
        
    def getSwitchState(self):
        return self._getState(StateType.SWITCH_STATE)[0]
    
    def getSwitchStateFloat(self):
        switchState = self._getState(StateType.SWITCH_STATE)[0]
        
        returnState = 0.0
        if switchState == 128:
            returnState = 1.0
        elif switchState <= 100:
            returnState = 0.01 * switchState * 0.99
        
        return returnState
    
    def getTime(self):
        bytesResult = self._getState(StateType.TIME)
        return Conversion.uint8_array_to_uint32(bytesResult)
    
    
    
    
    """
    ---------------  UTIL  ---------------
    """
    
    
    def _writeToState(self):
        pass
    
    def _getState(self, stateType):
        """
        :param stateType: StateType
        """
        result = self.core.ble.setupSingleNotification(CSServices.CrownstoneService, CrownstoneCharacteristics.StateRead, lambda: self._setState(stateType))
        length = Conversion.uint8_array_to_uint16([result[2], result[3]])
        
        state = []
        for i in range(0,length):
            state.append(result[i+4])
            
        return state
        
    
    def _setState(self, stateType):
        """
        :param stateType: StateType
        """
        self.core.ble.writeToCharacteristic(CSServices.CrownstoneService, CrownstoneCharacteristics.StateControl, ReadStatePacket(stateType).getPacket())