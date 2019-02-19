from BluenetLib._EventBusInstance import BluenetEventBus
from bluepy.btle import Scanner, DefaultDelegate

from BluenetLib.lib.packets.Advertisement import Advertisement
from BluenetLib.lib.topics.SystemBleTopics import SystemBleTopics

SERVICE_DATA_ADTYPE = 22
NAME_ADTYPE         = 8
FLAGS_ADTYPE        = 1

class ScanDelegate(DefaultDelegate):
    
    def __init__(self, settings):
        self.settings = settings
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        valueText = dev.getValueText(SERVICE_DATA_ADTYPE)
        nameText = dev.getValueText(NAME_ADTYPE)
        if valueText is not None:
            self.parsePayload(dev.addr, dev.rssi, nameText, valueText)
          
    def parsePayload(self, address, rssi, nameText, valueText):
        advertisement = Advertisement(address, rssi, nameText, valueText)
        if self.settings.encryptionEnabled:
            advertisement.decrypt(self.settings.guestKey)
            
        if advertisement.isCrownstoneFamily():
            BluenetEventBus.emit(SystemBleTopics.rawAdvertisement, advertisement)