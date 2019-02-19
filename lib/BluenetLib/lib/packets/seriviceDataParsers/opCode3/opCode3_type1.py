import time

from BluenetLib.lib.util.Timestamp import reconstructTimestamp
from BluenetLib.lib.util.Conversion import Conversion


def parseOpCode3_type1(serviceData, data):
    if len(data) == 17:
        # opCode = data[0]
        # dataType = data[1]
        
        serviceData.errorMode = True
        
        serviceData.crownstoneId = data[2]
        serviceData.errorsBitmask = Conversion.uint8_array_to_uint32([
            data[3],
            data[4],
            data[5],
            data[6]
        ])
        
        serviceData.errorTimestamp = Conversion.uint8_array_to_uint32([
            data[7],
            data[8],
            data[9],
            data[10]
        ])
        
        serviceData.flagsBitmask = data[11]
        # bitmask states
        bitmaskArray = Conversion.uint8_to_bit_array(serviceData.flagsBitmask)
        
        serviceData.dimmingAvailable   = bitmaskArray[0]
        serviceData.dimmingAllowed     = bitmaskArray[1]
        serviceData.hasError           = bitmaskArray[2]
        serviceData.switchLocked       = bitmaskArray[3]
        serviceData.timeIsSet          = bitmaskArray[4]
        serviceData.switchCraftEnabled = bitmaskArray[5]
        
        serviceData.temperature = Conversion.uint8_to_int8(data[12])

        serviceData.partialTimestamp = Conversion.uint8_array_to_uint16([data[13], data[14]])
        serviceData.uniqueIdentifier = serviceData.partialTimestamp

        if serviceData.timeIsSet:
            serviceData.timestamp = reconstructTimestamp(time.time(), serviceData.partialTimestamp)
        else:
            serviceData.timestamp = serviceData.partialTimestamp # this is now a counter
        
        realPower = Conversion.uint16_to_int16(
            Conversion.uint8_array_to_uint16([
                data[15],
                data[16]
            ])
        )
        
        serviceData.powerUsageReal = float(realPower) / 8.0
        
        # this packet has no validation
        serviceData.validation = 0
