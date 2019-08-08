import time
from threading import Timer

from DisplayBoard.DisplayDriver import DisplayDriver

class LoadingRunner:

    def __init__(self):
        self.loopPending = False
        self.executePending = False
        self.queue = []

        self.progress = 0
        self.active = False

        self.board = DisplayDriver()

    def __del__(self):
        self.stop()

    def setProgress(self, progress):
        """
        progress is between 0 and 1
        :param progress:
        :return:
        """
        self.progress = progress


    def start(self):
        self.active = True
        self.run()

    def stop(self):
        self.active = False
        self.waitToFinish()


    def run(self):
        if not self.executePending:
            self.executePending = True
            Timer(0.001, self.runBlocking, ()).start()


    def runBlocking(self):
        self.executePending = False
        self.loopPending = True

        while self.active:
            self._cycle([
                "LB",
                "LT",
                "T",
                "RT",
                "RB",
                "B",
            ], delay=0.04, loops=1)

            self.board.clearPersistedSlots()
            if self.progress >= 1/6:
                self.board.persistSlot("LB")

            if self.progress >= 2/6:
                self.board.persistSlot("LT")

            if self.progress >= 3/6:
                self.board.persistSlot("T")

            if self.progress >= 4/6:
                self.board.persistSlot("RT")

            if self.progress >= 5/6:
                self.board.persistSlot("RB")

            if self.progress >= 6/6:
                self.board.persistSlot("B")

        self.loopPending = False


    def _cycle(self, slotArray, delay=0.1, loops=1):
        for loop in range(0,loops):
            for slot in slotArray:
                self.board.clearDisplay()
                self.board.illuminateSlot([slot])
                time.sleep(delay)


    def isFinished(self):
        isRunning = self.loopPending or self.executePending
        return not isRunning


    def waitToFinish(self):
        while not self.isFinished():
            time.sleep(0.1)


