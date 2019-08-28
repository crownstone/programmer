from BluenetLib._EventBusInstance import BluenetEventBus

from BluenetLib.lib.packets.Advertisement import Advertisement
from BluenetLib.lib.packets.AioCrownstoneParser import AioCrownstoneParser
from BluenetLib.lib.topics.SystemBleTopics import SystemBleTopics


class AioScanDelegate:
    
    def __init__(self, settings):
        self.settings = settings

    def handleDiscovery(self, hciEvent):
        parsedCrownstoneData = AioCrownstoneParser(hciEvent)
        self.parsePayload(parsedCrownstoneData)

    def parsePayload(self, parsedCrownstoneData):
        advertisement = Advertisement(
            parsedCrownstoneData.address,
            parsedCrownstoneData.rssi,
            parsedCrownstoneData.name,
            parsedCrownstoneData.valueArr,
            parsedCrownstoneData.serviceUUID
        )

        if advertisement.serviceData.opCode <= 5:
            advertisement.decrypt(self.settings.basicKey)
        elif advertisement.serviceData.opCode >= 7:
            advertisement.decrypt(self.settings.serviceDataKey)

        print("parsing a packet", advertisement.isCrownstoneFamily())
        if advertisement.isCrownstoneFamily():
            BluenetEventBus.emit(SystemBleTopics.rawAdvertisement, advertisement)