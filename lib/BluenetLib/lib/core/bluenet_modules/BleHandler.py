from bluepy.btle import Scanner, Peripheral, ADDR_TYPE_RANDOM, BTLEException

from BluenetLib.Exceptions import BleError, BluenetBleException
from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.core.bluetooth_delegates.SingleNotificationDelegate import PeripheralDelegate
from BluenetLib.lib.core.bluetooth_delegates.ScanDelegate import ScanDelegate
from BluenetLib.lib.core.modules.Validator import Validator
from BluenetLib.lib.protocol.BluenetTypes import ProcessType
from BluenetLib.lib.topics.SystemBleTopics import SystemBleTopics
from BluenetLib.lib.util.EncryptionHandler import EncryptionHandler

from threading import Timer


CCCD_UUID = 0x2902

class BleHandler:
    
    def __init__(self, settings, hciIndex=0):
        self.connectedPeripherals = {}

        self.settings = None

        self.connectedPeripherals = {}
        self.connectedPeripheral = None

        self.notificationLoopActive = False
        self.notificationResult = None

        self.scanningActive = False
        self.scanAborted = False

        self.subscriptionIds = []
        
        self.validator = Validator()
        self.settings = settings
        self.hciIndex = hciIndex
        self.scanner = Scanner(self.hciIndex).withDelegate(ScanDelegate(settings))
        self.subscriptionIds.append(BluenetEventBus.subscribe(SystemBleTopics.abortScanning, lambda x: self.abortScanning()))
        
    
    def shutDown(self):
        for subscriptionId in self.subscriptionIds:
            BluenetEventBus.unsubscribe(subscriptionId)
            
        self.validator.shutDown()
    
    
    def connect(self, address):
        if address not in self.connectedPeripherals:
            self.connectedPeripherals[address] = Peripheral(iface=self.hciIndex)
            print("Connecting...")
            self.connectedPeripheral = address
            self.connectedPeripherals[address].connect(address, addrType=ADDR_TYPE_RANDOM, iface=self.hciIndex)
            self.connectedPeripherals[address].getServices()
            print("Connected")
            
    
    def disconnect(self):
        print("Disconnecting... Cleaning up")
        if self.connectedPeripheral:
            self.connectedPeripherals[self.connectedPeripheral].disconnect()
            del self.connectedPeripherals[self.connectedPeripheral]
            self.connectedPeripheral = None
            print("Cleaned up")
    
    
    def startScanning(self, scanDuration=3):
        if not self.scanningActive:
            self.scanner.start()
            self.scanningActive = True
            self.scanAborted = False
            scanTime = 0
            processInterval = 0.5
            while self.scanningActive and scanTime < scanDuration and not self.scanAborted:
                scanTime += processInterval
                self.scanner.process(processInterval)
            
            self.stopScanning()

    def startScanningBackground(self, scanDuration=3):
        Timer(0.0001, lambda: self.startScanning(scanDuration))

    
    def stopScanning(self):
        if self.scanningActive:
            self.scanner.stop()
            self.scanningActive = False
            
    def abortScanning(self):
        if self.scanningActive:
            self.scanAborted = True
    
    def enableNotifications(self):
        print("ENABLE NOTIFICATIONS IS NOT IMPLEMENTED YET")
    
    def disableNotifications(self):
        print("DISABLE NOTIFICATIONS IS NOT IMPLEMENTED YET")

    def writeToCharacteristic(self, serviceUUID, characteristicUUID, content):
        targetCharacteristic = self.getCharacteristic(serviceUUID, characteristicUUID)
        encryptedContent = EncryptionHandler.encrypt(content, self.settings)
        targetCharacteristic.write(encryptedContent, withResponse=True)


    def readCharacteristic(self, serviceUUID, characteristicUUID):
        data = self.readCharacteristicWithoutEncryption(serviceUUID, characteristicUUID)
        if self.settings.isEncryptionEnabled():
            return EncryptionHandler.decrypt(data, self.settings)


    def readCharacteristicWithoutEncryption(self, serviceUUID, characteristicUUID):
        targetCharacteristic = self.getCharacteristic(serviceUUID, characteristicUUID)
        data = targetCharacteristic.read()
        return data

    
    def getCharacteristic(self, serviceUUID, characteristicUUID):
        if self.connectedPeripheral:
            peripheral = self.connectedPeripherals[self.connectedPeripheral]
        
            try:
                service = peripheral.getServiceByUUID(serviceUUID)
            except BTLEException:
                raise BluenetBleException(BleError.CAN_NOT_FIND_SERVICE, "Can not find service: " + serviceUUID)
        
            characteristics = service.getCharacteristics(characteristicUUID)
            if len(characteristics) == 0:
                raise BluenetBleException(BleError.CAN_NOT_FIND_CHACTERISTIC, "Can not find characteristic: " + characteristicUUID)

            return characteristics[0]
        
        else:
            raise BluenetBleException(BleError.CAN_NOT_GET_CHACTERISTIC, "Can't get characteristic: Not connected.")
        
        
    def setupSingleNotification(self, serviceUUID, characteristicUUID, writeCommand):
        characteristic = self.getCharacteristic(serviceUUID, characteristicUUID)
        peripheral = self.connectedPeripherals[self.connectedPeripheral]
        
        peripheral.withDelegate(PeripheralDelegate(lambda x: self._killNotificationLoop(x), self.settings))
        
        characteristicCCCDList = characteristic.getDescriptors(forUUID=CCCD_UUID)
        if len(characteristicCCCDList) == 0:
            raise BluenetBleException(BleError.CAN_NOT_FIND_CCCD, "Can not find CCCD handle to use notifications for characteristic: " + characteristicUUID)
        
        characteristicCCCD = characteristicCCCDList[0]
        
        # enable notifications.. This is ugly but necessary
        characteristicCCCD.write(b"\x01\x00", True)
        
        # execute something that will trigger the notifications
        writeCommand()
        
        self.notificationLoopActive = True

        loopCount = 0
        while self.notificationLoopActive and loopCount < 10:
            peripheral.waitForNotifications(0.5)
            loopCount += 1


        if self.notificationResult is None:
            raise BluenetBleException(BleError.NO_NOTIFICATION_DATA_RECEIVED, "No notification data received.")
        
        result = self.notificationResult
        self.notificationResult = None
        
        return result
    
    def setupNotificationStream(self, serviceUUID, characteristicUUID, writeCommand, resultHandler, timeout):
        characteristic = self.getCharacteristic(serviceUUID, characteristicUUID)
        peripheral = self.connectedPeripherals[self.connectedPeripheral]
        
        peripheral.withDelegate(PeripheralDelegate(lambda x: self._loadNotificationResult(x), self.settings))
    
        characteristicCCCDList = characteristic.getDescriptors(forUUID=CCCD_UUID)
        if len(characteristicCCCDList) == 0:
            raise BluenetBleException(BleError.CAN_NOT_FIND_CCCD, "Can not find CCCD handle to use notifications for characteristic: " + characteristicUUID)
    
        characteristicCCCD = characteristicCCCDList[0]
    
        # enable notifications.. This is ugly but necessary
        characteristicCCCD.write(b"\x01\x00", True)
    
        # execute something that will trigger the notifications
        writeCommand()
    
        self.notificationLoopActive = True
        self.notificationResult = None
        
        loopCount = 0
        successful = False
        while self.notificationLoopActive and loopCount < timeout*2:
            peripheral.waitForNotifications(0.5)
            loopCount += 1
            if self.notificationResult is not None:
                command = resultHandler(self.notificationResult)
                self.notificationResult = None
                if command == ProcessType.ABORT_ERROR:
                    self.notificationLoopActive = False
                    raise BluenetBleException(BleError.ABORT_NOTIFICATION_STREAM_W_ERROR, "Aborting the notification stream because the resultHandler raised an error.")
                elif command == ProcessType.FINISHED:
                    self.notificationLoopActive = False
                    successful = True
    
        if not successful:
            raise BluenetBleException(BleError.NOTIFICATION_STREAM_TIMEOUT, "Notification stream not finished within timeout.")
    
        
    def _killNotificationLoop(self, result):
        self.notificationLoopActive = False
        self.notificationResult = result
        
    def _loadNotificationResult(self, result):
        self.notificationResult = result
    