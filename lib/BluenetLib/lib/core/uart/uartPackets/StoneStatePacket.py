import time

from BluenetLib.lib.packets.CrownstoneErrors import CrownstoneErrors

from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.util.Conversion import Conversion
from BluenetLib.lib.util.Timestamp  import reconstructTimestamp

STONE_STATE_PACKET_SIZE = 14

class StoneStatePacket:

    def __init__(self, meshStateItem):
        self.type = 0
        self.crownstoneId = 0
        self.switchState = 0
        self.flagsBitmask = 0
        self.temperature = 0
        self.powerFactor = 0
        self.powerUsageReal = 0
        self.powerUsageApparent = 0
        self.accumulatedEnergy = 0
        self.partialTimestamp = 0
        self.timestamp = 0
        self.deprecated = False
        
        self.hasError = False
        self.errorMode = False
        self.errorsBitmask = 0
        self.errorTimestamp = 0
        
        self.dimmingAvailable   = False
        self.dimmingAllowed     = False
        self.hasError           = False
        self.switchLocked       = False
        self.timeIsSet          = False
        self.switchCraftEnabled = False
        
        if len(meshStateItem) != STONE_STATE_PACKET_SIZE:
            print("ERROR: Invalid length of StoneStatePacket", len(meshStateItem), meshStateItem)

        self.type = meshStateItem[0]

        if self.type is 0 or self.type is 2:
            self.parseState(meshStateItem[1:])
        else:
            self.parseErrorState(meshStateItem[1:])

        bitmaskArray = Conversion.uint8_to_bit_array(self.flagsBitmask)

        self.dimmingAvailable   = bitmaskArray[0]
        self.dimmingAllowed     = bitmaskArray[1]
        self.hasError           = bitmaskArray[2]
        self.switchLocked       = bitmaskArray[3]
        self.timeIsSet          = bitmaskArray[4]
        self.switchCraftEnabled = bitmaskArray[5]


    def parseErrorState(self, meshErrorState):
        self.crownstoneId = meshErrorState[0]
        self.hasError = True
        self.errorMode = True
        
        self.errorsBitmask = Conversion.uint8_array_to_uint32([
            meshErrorState[1],
            meshErrorState[2],
            meshErrorState[3],
            meshErrorState[4]
        ])
        
        self.errorTimestamp = Conversion.uint8_array_to_uint32([
            meshErrorState[5],
            meshErrorState[6],
            meshErrorState[7],
            meshErrorState[8]
        ])
        
        self.flagsBitmask = meshErrorState[9]
        self.temperature = meshErrorState[10]

        self.partialTimestamp = Conversion.uint8_array_to_uint16(meshErrorState[11:13])
        self.timestamp = reconstructTimestamp(time.time(), self.partialTimestamp)
    
        if self.crownstoneId == 0:
            self.deprecated = True

    def parseState(self, meshStateItemState):
        self.crownstoneId       = meshStateItemState[0]
        self.switchState        = meshStateItemState[1]
        self.flagsBitmask        = meshStateItemState[2]
        self.temperature        = meshStateItemState[3]
        self.powerFactor        = float(meshStateItemState[4]) / 127
        self.powerUsageReal     = float(Conversion.uint8_array_to_int16(meshStateItemState[5:7])) / 8
        if self.powerFactor == 0:
            self.powerFactor = 1.0
        self.powerUsageApparent = self.powerUsageReal / self.powerFactor
        self.accumulatedEnergy         = Conversion.uint8_array_to_int32(meshStateItemState[7:11])
        self.partialTimestamp   = Conversion.uint8_array_to_uint16(meshStateItemState[11:13])
        self.timestamp          = reconstructTimestamp(time.time(), self.partialTimestamp)

        if self.crownstoneId == 0:
            self.deprecated = True
            
        

    def constuctTimestamp(self):
        pass

    def broadcastState(self):
        if self.deprecated:
            return

        # tell the system this advertisement.
        BluenetEventBus.emit(SystemTopics.stateUpdate, (self.crownstoneId, self))

    def getDict(self):
        data = {}

        data["id"]                 = self.crownstoneId
        data["switchState"]        = self.switchState
        data["flagBitMask"]        = self.flagsBitmask
        data["temperature"]        = self.temperature
        data["powerFactor"]        = self.powerFactor
        data["powerUsageReal"]     = self.powerUsageReal
        data["powerUsageApparent"] = self.powerUsageApparent
        data["accumulatedEnergy"]  = self.accumulatedEnergy
        data["timestamp"]          = self.timestamp

        return data
    
    def getSummary(self):
        errorsDictionary = CrownstoneErrors(self.errorsBitmask).getDictionary()
    
        returnDict = {}

        returnDict["id"] = self.crownstoneId
        returnDict["setupMode"] = False # its always false if it comes over mesh: setup haz no mesh.
        returnDict["switchState"] = self.switchState
        returnDict["temperature"] = self.temperature
        returnDict["powerFactor"] = self.powerFactor
        returnDict["powerUsageReal"] = self.powerUsageReal
        returnDict["powerUsageApparent"] = self.powerUsageApparent
        returnDict["accumulatedEnergy"] = self.accumulatedEnergy
        returnDict["dimmingAvailable"] = self.dimmingAvailable
        returnDict["dimmingAllowed"] = self.dimmingAllowed
        returnDict["switchLocked"] = self.switchLocked
        returnDict["switchCraftEnabled"] = self.switchCraftEnabled
        returnDict["timeIsSet"] = self.timeIsSet
        returnDict["timestamp"] = self.timestamp
        returnDict["hasError"] = self.hasError
        returnDict["errorMode"] = self.errorMode
        returnDict["errors"] = errorsDictionary
        
        return returnDict

        