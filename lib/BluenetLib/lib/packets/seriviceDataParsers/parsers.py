from BluenetLib.lib.util.Conversion import Conversion

from BluenetLib.lib.packets.seriviceDataParsers.opCode3.opCode3_type0 import parseOpCode3_type0
from BluenetLib.lib.packets.seriviceDataParsers.opCode3.opCode3_type1 import parseOpCode3_type1
from BluenetLib.lib.packets.seriviceDataParsers.opCode3.opCode3_type2 import parseOpCode3_type2
from BluenetLib.lib.packets.seriviceDataParsers.opCode3.opCode3_type3 import parseOpCode3_type3
from BluenetLib.lib.protocol.BluenetTypes import DeviceType


def parseOpCode3(serviceData, data):
    if len(data) == 16:
        serviceData.dataType = data[0]
        if serviceData.dataType == 0:
            parseOpCode3_type0(serviceData, data)
        elif serviceData.dataType == 1:
            parseOpCode3_type1(serviceData, data)
        elif serviceData.dataType == 2:
            parseOpCode3_type2(serviceData, data)
        elif serviceData.dataType == 3:
            parseOpCode3_type3(serviceData, data)
        else:
            parseOpCode3_type0(serviceData, data)





from BluenetLib.lib.packets.seriviceDataParsers.opCode4.opCode4_type0 import parseOpCode4_type0

def parseOpCode4(serviceData, data):
    if len(data) == 16:
        serviceData.dataType = data[0]
        serviceData.setupMode = True
        if serviceData.dataType == 0:
            parseOpCode4_type0(serviceData, data)
        else:
            parseOpCode4_type0(serviceData, data)


def parseOpCode5(serviceData, data):
    if len(data) == 16:
        serviceData.dataType = data[0]

        if serviceData.dataType == 0:
            parseOpCode3_type0(serviceData, data)
        elif serviceData.dataType == 1:
            parseOpCode3_type1(serviceData, data)
        elif serviceData.dataType == 2:
            parseOpCode3_type2(serviceData, data)
            serviceData.rssiOfExternalCrownstone = Conversion.uint8_to_int8(data[15])
        elif serviceData.dataType == 3:
            parseOpCode3_type3(serviceData, data)
            serviceData.rssiOfExternalCrownstone = Conversion.uint8_to_int8(data[15])
        else:
            parseOpCode3_type0(serviceData, data)


def parseOpCode6(serviceData, data):
    if len(data) == 16:
        serviceData.dataType = data[0]
    
        serviceData.setupMode = True
        
        if serviceData.dataType == 0:
            parseOpCode4_type0(serviceData, data)
        else:
            parseOpCode4_type0(serviceData, data)
        


