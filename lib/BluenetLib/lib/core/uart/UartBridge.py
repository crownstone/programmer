import threading

import serial

from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.core.uart.UartParser import UartParser
from BluenetLib.lib.core.uart.UartReadBuffer import UartReadBuffer
from BluenetLib.lib.topics.SystemTopics import SystemTopics


class UartBridge (threading.Thread):

    def __init__(self, port, baudrate):
        self.baudrate = baudrate
        self.port = port

        self.serialController = None
        self.parser = None
        self.eventId = 0
        
        self.running = True

        self.startSerial()
        threading.Thread.__init__(self)


    def run(self):
        self.eventId = BluenetEventBus.subscribe(SystemTopics.uartWriteData, self.writeToUart)
        
        BluenetEventBus.subscribe(SystemTopics.cleanUp, lambda x: self.stop())
        
        self.parser = UartParser()
        self.startReading()

    def stop(self):
        print("Stopping UartBridge")
        self.running = False
        BluenetEventBus.unsubscribe(self.eventId)
    
    def startSerial(self):
        print("Initializing serial on port ", self.port, ' with baudrate ', self.baudrate)
        self.serialController = serial.Serial()
        self.serialController.port = self.port
        self.serialController.baudrate = int(self.baudrate)
        self.serialController.timeout = None
        self.serialController.open()


    def startReading(self):
        readBuffer = UartReadBuffer()
        print("Read starting on serial port.")
        while self.running:
            bytes = self.serialController.read()
            if bytes:
                # clear out the entire read buffer
                if self.serialController.in_waiting > 0:
                    additionalBytes = self.serialController.read(self.serialController.in_waiting)
                    bytes = bytes + additionalBytes
                readBuffer.addByteArray(bytes)

        print("Cleaning up")
        self.serialController.close()

    def writeToUart(self, data):
        self.serialController.write(data)
