from BluenetLib.lib.packets.ServiceData import ServiceData
from BluenetLib.lib.protocol.Services import DFU_ADVERTISEMENT_SERVICE_UUID
from BluenetLib.lib.util.Conversion import Conversion

class Advertisement:
    
    def __init__(self, address, rssi, nameText, serviceDataText):
        self.address = address
        self.rssi = rssi
        self.name = nameText

        self.serviceUUID = None
        self.serviceData = None
        self.operationMode = None

        dataString = serviceDataText
        
        if serviceDataText is not None:
            dataArray = Conversion.hex_string_to_uint8_array(dataString)
            self.serviceUUID = Conversion.uint8_array_to_uint16([dataArray[0], dataArray[1]])
            # pop the service UUID
            dataArray.pop(0)
            dataArray.pop(0)
            
            if serviceDataText:
                self.serviceData = ServiceData(dataArray)
    
            self.operationMode = "NORMAL"

    
    def isInDFUMode(self):
        return False
    
    def isInSetupMode(self):
        if self.serviceData is not None:
            return self.serviceData.setupMode
        return False
    
    def isCrownstoneFamily(self):
        return self.serviceUUID == 0xC001 or self.serviceUUID == 0xC002 or self.serviceUUID == 0xC003 or self.serviceUUID == DFU_ADVERTISEMENT_SERVICE_UUID

    def hasScanResponse(self):
        return self.serviceData is not None
    
    def getCrownstoneId(self):
        if self.hasScanResponse() and self.isCrownstoneFamily():
            return self.serviceData.crownstoneId
    
    def decrypt(self, key):
        if self.serviceData:
            self.serviceData.decrypt(key)
            
    def getDictionary(self):
        data = {}
    
        data["name"] = self.name
        data["rssi"] = self.rssi
        data["address"] = self.address
        
        if self.serviceUUID is not None:
            data["serviceUUID"] = self.serviceUUID
            
        if self.serviceData is not None:
            data["serviceData"] = self.serviceData.getDictionary()
    
        return data
    
    def getSummary(self):
        data = {}
        if self.serviceData is not None:
            data = self.serviceData.getSummary()
        return data

    
