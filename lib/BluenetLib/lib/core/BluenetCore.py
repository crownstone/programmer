import signal  # used to catch control C

from BluenetLib.CrownstoneCloud import CrownstoneCloud

from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.core.bluenet_modules.UsbDevHandler import UsbDevHandler
from BluenetLib.lib.core.uart.UartBridge import UartBridge
from BluenetLib.lib.core.uart.UartTypes import UartTxType
from BluenetLib.lib.core.uart.UartWrapper import UartWrapper
from BluenetLib.lib.dataFlowManagers.StoneManager import StoneManager
from BluenetLib.lib.protocol.BlePackets import ControlPacket
from BluenetLib.lib.protocol.BluenetTypes import IntentType, MeshMultiSwitchType, ControlType
from BluenetLib.lib.protocol.MeshPackets import StoneMultiSwitchPacket, MeshMultiSwitchPacket
from BluenetLib.lib.topics.SystemTopics import SystemTopics



class BluenetCore:

    def __init__(self, catchSIGINT=True):
        self.uartBridge = None
        self.running = True
        self.stoneManager = StoneManager()
        self._usbDev = UsbDevHandler()
        
        # listen for CTRL+C and handle the exit cleanly.
        if catchSIGINT:
            signal.signal(signal.SIGINT, self.__stopAll)

    def initializeUSB(self, port, baudrate=230400):
        # init the uart bridge
        self.uartBridge = UartBridge(port, baudrate)
        self.uartBridge.start()


    def __stopAll(self, source, frame):
        self.stop()
        
        

    def stop(self):
        print("Quitting BluenetLib...")
        BluenetEventBus.emit(SystemTopics.cleanUp)
        self.running = False


    def switchCrownstone(self, crownstoneId, on):
        """
        :param crownstoneId:
        :param on: Boolean
        :return:
        """
        state = 1
        if not on:
            state = 0

        self.__switchCrownstone(crownstoneId, state)


    def dimCrownstone(self, crownstoneId, value):
        # dimming is used when the value is [0 .. 99], 100 is turning on the relay. We map 0..1 to 0..0.99
        value = min(0.99, max(0,value) * 0.99)

        self.__switchCrownstone(crownstoneId, value)


    def getCrownstoneIds(self):
        return self.stoneManager.getIds()
    
    def getCrownstones(self):
        return self.stoneManager.getStones()

    def isRunning(self):
        return self.running

    def uartEcho(self, payloadString):
        # wrap that in a control packet
        controlPacket = ControlPacket(ControlType.UART_MESSAGE).loadString(payloadString).getPacket()
    
        # finally wrap it in an Uart packet
        uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()

        # send over uart
        BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)

    # MARK: Private

    def __switchCrownstone(self, crownstoneId, value):
        """
        :param crownstoneId:
        :param value: 0 .. 1
        :return:
        """

        # forcibly map the input from [any .. any] to [0 .. 1]
        correctedValue = min(1,max(0,value))

        # create a stone switch state packet to go into the multi switch
        stoneSwitchPacket     = StoneMultiSwitchPacket(crownstoneId, correctedValue, 0, IntentType.MANUAL)

        # wrap it in a mesh multi switch packet
        meshMultiSwitchPacket = MeshMultiSwitchPacket(MeshMultiSwitchType.SIMPLE_LIST, [stoneSwitchPacket]).getPacket()

        # wrap that in a control packet
        controlPacket         = ControlPacket(ControlType.MESH_MULTI_SWITCH).loadByteArray(meshMultiSwitchPacket).getPacket()

        # finally wrap it in an Uart packet
        uartPacket            = UartWrapper(UartTxType.CONTROL, controlPacket).getPacket()

        # send over uart
        BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)