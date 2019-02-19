import asyncio
from threading import Timer

import RPi.GPIO as GPIO
from DisplayBoard.LedDriver import LedDriver


class LedController:

    def __init__(self):
        self.loopPending = False
        self.executePending = False
        self.queue = []

        self.active = False

        self.led = LedDriver()
        self.led.start()

        self.interval = 0.4

        self.ledSolidOn     = False
        self.loop        = asyncio.new_event_loop()
        self.closingLoop = asyncio.new_event_loop()


    def off(self):
        self.led.turnLedOff()
        self.stop()
        self.led.turnLedOff()

    def on(self):
        self.led.turnLedOn()
        self.ledSolidOn = True

    def startBlinking(self):
        self.ledSolidOn = False
        if not self.active:
            self.active = True
            self.run()

    def solidOn(self):
        self.ledSolidOn = True

    def blink(self):
        self.ledSolidOn = False
        self.interval = 0.4
        self.startBlinking()

    def blinkFast(self):
        self.ledSolidOn = False
        self.interval = 0.1
        self.startBlinking()

    def setBlinkInterval(self, interval):
        self.interval = interval
        if not self.active:
            self.blink()

    def stop(self):
        print("Stopping LED controller")
        self.active = False
        self.closingLoop.run_until_complete(self.waitToFinish())
        print("Stopped LED controller")

    def cleanup(self):
        self.led.cleanup()

    def run(self):
        if not self.executePending:
            self.executePending = True
            print("start Led controller loop")
            Timer(0.001, self.runBlocking, ()).start()


    def runBlocking(self):
        self.executePending = False
        self.loopPending = True

        while self.active:
            if self.ledSolidOn:
                self.loop.run_until_complete(self._cycle([1]))
            else:
                self.loop.run_until_complete(self._cycle([1,0]))

        self.loopPending = False


    async def _cycle(self, stateArray):
        for state in stateArray:
            self.led.setLED(state)
            await asyncio.sleep(self.interval)


    def isFinished(self):
        isRunning = self.loopPending or self.executePending
        return not isRunning


    async def waitToFinish(self):
        while not self.isFinished():
            await asyncio.sleep(0.1)



























