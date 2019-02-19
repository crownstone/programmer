from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.topics.UsbTopics import UsbTopics


class StoneStateManager:
    def __init__(self):
        self.stones = {}
        BluenetEventBus.subscribe(SystemTopics.stateUpdate, self.handleStateUpdate)

    def handleStateUpdate(self,data):
        stoneId = data[0]
        stoneStatePacket = data[1]

        if stoneId in self.stones:
            if self.stones[stoneId]["timestamp"] < stoneStatePacket.timestamp:
                self.stones[stoneId] = stoneStatePacket.getSummary()
                self.emitNewData(stoneStatePacket)
        else:
            BluenetEventBus.emit(SystemTopics.newCrownstoneFound, stoneId)
            self.stones[stoneId] = stoneStatePacket.getSummary()
            self.emitNewData(stoneStatePacket)
    
    def emitNewData(self, stoneStatePacket):
        BluenetEventBus.emit(UsbTopics.newDataAvailable, stoneStatePacket.getSummary())

    def getIds(self):
        ids = []
        for stoneId, stoneData in self.stones.items():
            ids.append(stoneId)

        return ids
