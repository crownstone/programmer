
from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.core.modules.StoneAdvertisementTracker import StoneAdvertisementTracker
from BluenetLib.lib.topics.SystemBleTopics import SystemBleTopics
from BluenetLib.lib.topics.Topics import Topics

import threading

class Validator:

    def __init__(self):
        BluenetEventBus.subscribe(SystemBleTopics.rawAdvertisement, self.checkAdvertisement)
        self.tickTimer = None
        self._lock = threading.Lock()
        self.scheduleTick()
        self.trackedCrownstones = {}


    def scheduleTick(self):
        if self.tickTimer is not None:
            self.tickTimer.cancel()

        self.tickTimer = threading.Timer(1, lambda: self.tick())
        self.tickTimer.start()


    def tick(self):
        with self._lock:
            allKeys = []
            # we first collect keys because we might delete items from this list during ticks
            for key, trackedStone in self.trackedCrownstones.items():
                allKeys.append(key)

            for key in allKeys:
                self.trackedCrownstones[key].tick()

        self.scheduleTick()


    def removeStone(self, address):
        del self.trackedCrownstones[address]


    def checkAdvertisement(self, advertisement):
        if advertisement.address not in self.trackedCrownstones:
            self.trackedCrownstones[advertisement.address] = StoneAdvertisementTracker(lambda: self.removeStone(advertisement.address))
        
        self.trackedCrownstones[advertisement.address].update(advertisement)
        
        if self.trackedCrownstones[advertisement.address].verified:
            BluenetEventBus.emit(Topics.advertisement, advertisement.getDictionary())
            
            if advertisement.hasScanResponse:
                BluenetEventBus.emit(Topics.newDataAvailable, advertisement.getSummary())


    def shutDown(self):
        if self.tickTimer is not None:
            self.tickTimer.cancel()
