from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.topics.SystemBleTopics import SystemBleTopics


class SetupChecker:

    def __init__(self, address, waitUntilInRequiredMode=False):
        self.address = address
        self.result = False
        self.waitUntilInRequiredMode = waitUntilInRequiredMode

    def handleAdvertisement(self, advertisement):
        if "serviceData" not in advertisement:
            return

        if advertisement["address"] != self.address:
            return

        self.result = advertisement["serviceData"]["setupMode"]

        if not self.result and self.waitUntilInRequiredMode:
            pass
        else:
            BluenetEventBus.emit(SystemBleTopics.abortScanning, True)

    def getResult(self):
        return self.result

