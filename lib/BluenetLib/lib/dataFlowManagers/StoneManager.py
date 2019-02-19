from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.dataFlowManagers.StoneStateManager import StoneStateManager
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.topics.SystemCloudTopics import SystemCloudTopics


class StoneManager:
    
    def __init__(self):
        self.stones = {}
        self.stateManager = StoneStateManager()
        BluenetEventBus.subscribe(SystemTopics.newCrownstoneFound, self.handleNewStoneFromScan)
        BluenetEventBus.subscribe(SystemCloudTopics.stoneDownloadedFromCloud, self.handleStoneFromCloud)
        
        
    def getIds(self):
        ids = []
        for stoneId, data in self.stones.items():
            ids.append(stoneId)

        return ids
    
    
    def getStones(self):
        return self.stones
    
    
    def handleNewStoneFromScan(self, stoneId):
        if stoneId in self.stones:
            self.stones[stoneId]["available"] = True
        else:
            self.stones[stoneId] = {"available": True, "id": stoneId}
            
        # BluenetEventBus.emit(Topics.crownstoneAvailable, self.stones[stoneId])
        
            
    def handleStoneFromCloud(self, stoneData):
        stoneId = stoneData["id"]
        
        available = False
        if stoneId in self.stones:
            available = self.stones[stoneId]["available"]
        
        self.stones[stoneId] = stoneData
        self.stones[stoneId]["available"] = available
        
