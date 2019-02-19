import time

from BluenetLib.lib.util.Conversion import Conversion
from BluenetLib.lib.util.Timestamp import reconstructTimestamp


def parseOpCode3_type0(serviceData, data):
    if len(data) == 17:
        # opCode = data[0]
        # dataType = data[1]
        
        serviceData.stateOfExternalCrownstone = False
        
        serviceData.crownstoneId = data[2]
        serviceData.switchState  = data[3]
        serviceData.flagsBitmask = data[4]
        
        # bitmask states
        bitmaskArray = Conversion.uint8_to_bit_array(serviceData.flagsBitmask)
        
        serviceData.dimmingAvailable   = bitmaskArray[0]
        serviceData.dimmingAllowed     = bitmaskArray[1]
        serviceData.hasError           = bitmaskArray[2]
        serviceData.switchLocked       = bitmaskArray[3]
        serviceData.timeIsSet          = bitmaskArray[4]
        serviceData.switchCraftEnabled = bitmaskArray[5]
        
        serviceData.temperature        = Conversion.uint8_to_int8(data[5])
        powerFactor                    = Conversion.uint8_to_int8(data[6])
        realPower                      = Conversion.uint16_to_int16(Conversion.uint8_array_to_uint16([data[7], data[8]]))
        
        serviceData.powerFactor = float(powerFactor) / 127.0
        
        # we cannot have a 0 for a power factor.To avoid division by 0, we set it to be either 0.01 or -0.01
        if 0 <= serviceData.powerFactor < 0.01:
            serviceData.powerFactor = 0.01
        elif -0.01 < serviceData.powerFactor < 0:
            serviceData.powerFactor = -0.01
        
        serviceData.powerUsageReal = float(realPower) / 8.0
        serviceData.powerUsageApparent = serviceData.powerUsageReal / serviceData.powerFactor
        
        serviceData.accumulatedEnergy = Conversion.uint32_to_int32(
            Conversion.uint8_array_to_uint32([
                data[9],
                data[10],
                data[11],
                data[12]
            ])
        )
        
        serviceData.partialTimestamp = Conversion.uint8_array_to_uint16([data[13], data[14]])
        serviceData.uniqueIdentifier = serviceData.partialTimestamp
        
        if serviceData.timeIsSet:
            serviceData.timestamp = reconstructTimestamp(time.time(), serviceData.partialTimestamp)
        else:
            serviceData.timestamp = serviceData.partialTimestamp # this is now a counter
        
        
        serviceData.validation = data[16]

    

