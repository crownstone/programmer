from BluenetLib.lib.protocol.BluenetTypes import ControlType, ResultValue
from BluenetLib.lib.util.Conversion import Conversion


class ResultPacket:
    
    def __init__(self, data) :
        self.commandType = ControlType.UNSPECIFIED
        self.size = 0
        self.commandTypeUInt16 = 0
        self.resultCode = 0
        self.valid = False

        self.payload = []
        self.load(data)
    

    def load(self, data) :
        minSize = 6

        if len(data) >= minSize:
            self.commandTypeUInt16 = Conversion.uint8_array_to_uint16([data[0], data[1]])
            resultNumber  = Conversion.uint8_array_to_uint16([data[2], data[3]])

            if ControlType.has_value(self.commandTypeUInt16) and ResultValue.has_value(resultNumber):
                self.commandType = ControlType(self.commandTypeUInt16)
                self.resultCode  = ResultValue(resultNumber)
                self.size        = Conversion.uint8_array_to_uint16([data[4], data[5]])

                totalSize = minSize + self.size
                if len(data) >= totalSize:
                    if self.size == 0:
                        return

                    for i in range(minSize, totalSize):
                        self.payload.append(data[i])
                else:
                    self.valid = False
            else:
                self.valid = False
        else:
            self.valid = False