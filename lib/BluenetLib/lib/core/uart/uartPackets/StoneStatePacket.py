import time

from BluenetLib.lib.packets.CrownstoneErrors import CrownstoneErrors

from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.util.Conversion import Conversion
from BluenetLib.lib.util.Timestamp  import reconstructTimestamp

STONE_STATE_PACKET_SIZE = 14

class StoneStatePacket:

    def __init__(self, serviceData):
        self.serviceData = serviceData

    def broadcastState(self):
        # tell the system this advertisement.
        BluenetEventBus.emit(SystemTopics.stateUpdate, (self.serviceData.crownstoneId, self))

    def getDict(self):

        return self.serviceData.getDictionary()
    
    def getSummary(self):
        errorsDictionary = CrownstoneErrors(self.serviceData.errorsBitmask).getDictionary()
    
        returnDict = {}

        returnDict["id"] = self.serviceData.crownstoneId
        returnDict["setupMode"] = False # its always false if it comes over mesh: setup haz no mesh.
        returnDict["switchState"] = self.serviceData.switchState
        returnDict["temperature"] = self.serviceData.temperature
        returnDict["powerFactor"] = self.serviceData.powerFactor
        returnDict["powerUsageReal"] = self.serviceData.powerUsageReal
        returnDict["powerUsageApparent"] = self.serviceData.powerUsageApparent
        returnDict["accumulatedEnergy"] = self.serviceData.accumulatedEnergy
        returnDict["dimmerReady"] = self.serviceData.dimmerReady
        returnDict["dimmingAllowed"] = self.serviceData.dimmingAllowed
        returnDict["switchLocked"] = self.serviceData.switchLocked
        returnDict["switchCraftEnabled"] = self.serviceData.switchCraftEnabled
        returnDict["timeIsSet"] = self.serviceData.timeIsSet
        returnDict["timestamp"] = self.serviceData.timestamp
        returnDict["hasError"] = self.serviceData.hasError
        returnDict["errorMode"] = self.serviceData.errorMode
        returnDict["errors"] = errorsDictionary
        
        return returnDict

        