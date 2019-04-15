from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.topics.SystemBleTopics import SystemBleTopics


class RssiChecker:

    def __init__(self, address):
        self.address = address
        self.result = []

    def handleAdvertisement(self, advertisement):
        if "serviceData" not in advertisement:
            return

        if advertisement["address"] != self.address:
            return

        self.result.append(advertisement["rssi"])


    def getResult(self):
        sum = 0
        for res in self.result:
            sum += res
        return sum/len(self.result)


