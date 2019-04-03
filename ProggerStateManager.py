from util import path
import sys, os

from ButtonWatcher.ButtonWatcher import ButtonWatcher
from DisplayBoard.LedController import LedController
from DisplayBoard.LedDriver import LedDriver
import time, signal, subprocess
from config import TEST_RUNNER_PATH

from subprocess import Popen, PIPE


class ProggerStateManager:
    buttonWatcher = None
    ledController = None

    running = False

    testsActivated = False
    lidClosed = None

    session = None

    def __init__(self):
        print("watchers initiated")
        self.buttonWatcher = ButtonWatcher()
        self.ledController = LedController()

        self.buttonWatcher.start()
        self.ledController.startBlinking()

        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        self.running = True
        self.run()


    def run(self):
        while self.running:
            if self.buttonWatcher.buttonState == True and self.buttonWatcher.lidClosed == True:
                # button pressed
                if not self.testsActivated:
                    print("Starting test!")
                    self.runTest()
                    self.ledController.solidOn()

            if self.buttonWatcher.lidClosed != self.lidClosed:
                self.lidClosed = self.buttonWatcher.lidClosed
                if self.lidClosed:
                    print("Lid is closed.")
                    self.ledController.blinkFast()
                else:
                    print("Lid is open.")
                    self.killTests()
                    self.testsActivated = False
                    self.ledController.blink()

            time.sleep(0.1)

    def runTest(self):
        self.testsActivated = True
        self.session = subprocess.Popen(["sudo", "python3", TEST_RUNNER_PATH], preexec_fn=os.setsid)


    def killTests(self):
        self.ledController.blink()
        if self.session is not None:
            print("ProggerStateManager: Terminating tests...")
            self.session.terminate()
            try:
                print("ProggerStateManager: Waiting for tests to terminate...")
                self.session.wait(3)
                print("ProggerStateManager: Terminated.")
            except:
                print("ProggerStateManager: Forced to kill the tests....")
                self.session.kill()
                time.sleep(3)
            self.session = None


    def cleanup(self, source=None, frame=None):
        """
        Triggered by a kill command
        :param source:
        :param frame:
        :return:
        """
        print("Cleaning up the ProggerStateManager")
        # stop tests
        self.killTests()

        # stop main loop
        self.running = False

        # stop threads
        self.ledController.stop()
        self.buttonWatcher.stop()

        # cleanup used gpio
        self.buttonWatcher.cleanup()
        self.ledController.cleanup()

        time.sleep(1)

        quit()


if __name__ == "__main__":
    a = ProggerStateManager()