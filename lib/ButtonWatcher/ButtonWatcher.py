import asyncio, sys, signal
from threading import Timer
import RPi.GPIO as GPIO

from getPinLayout import GPIO_TO_PIN, BOARD_TO_GPIO


class ButtonWatcher:
    buttonPin = GPIO_TO_PIN[BOARD_TO_GPIO["BUTTON"]]
    lidPin    = GPIO_TO_PIN[BOARD_TO_GPIO["LID"]]

    buttonState = False
    lidClosed   = False

    executePending = False
    loopPending = False
    active = False

    def __init__(self, catchSignal=False):
        self.loop        = asyncio.new_event_loop()
        self.closingLoop = asyncio.new_event_loop()

        if catchSignal:
            signal.signal(signal.SIGINT, self._end)
            signal.signal(signal.SIGTERM, self._end)

    def _end(self, source=None, frame=None):
        self.stop()
        self.cleanup()

    def start(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.buttonPin, GPIO.IN)
        GPIO.setup(self.lidPin, GPIO.IN)
        if not self.active:
            self.active = True
            self.run()

    def cleanup(self):
        GPIO.cleanup([self.buttonPin, self.lidPin])


    def stop(self):
        print("Stopping button watcher")
        self.active = False
        self.closingLoop.run_until_complete(self.waitToFinish())
        print("button watcher stopped")

    def run(self):
        if not self.executePending:
            self.executePending = True
            print("start button watcher loop")
            Timer(0.001, self.runBlocking, ()).start()


    def runBlocking(self):
        self.executePending = False
        self.loopPending = True

        while self.active:
            self.loop.run_until_complete(self.checkButtonStates())

        self.loopPending = False


    async def checkButtonStates(self):
        self.buttonState = not GPIO.input(self.buttonPin)
        self.lidClosed = GPIO.input(self.lidPin) == 1
        await asyncio.sleep(0.1)


    def isFinished(self):
        isRunning = self.loopPending or self.executePending
        return not isRunning

    async def waitToFinish(self):
        while not self.isFinished():
            await asyncio.sleep(0.1)




if __name__ == "__main__":
    a = ButtonWatcher(True)
    a.start()



















