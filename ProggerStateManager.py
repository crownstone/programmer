from util import path
import sys, os

from ButtonWatcher.ButtonWatcher import ButtonWatcher
from DisplayBoard.LedController import LedController
from DisplayBoard.LedDriver import LedDriver
import time, signal, subprocess, traceback
from config import TEST_RUNNER_PATH

from subprocess import Popen, PIPE


class ProggerStateManager:
    """
    This class is responsible:
    - monitoring open/closed state of lid
    - operating the status led
    - launching/killing the sub process of the Test Runner.
    """

    def __init__(self):
        self.testsActivated = False
        self.lidClosed = None

        # handle to the sub process for the tests.
        self.session = None

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
        """
        Starts test on button press (if not yet started).
        Checks if lid is closed and kill tests if not.
        """
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
                    print("Lid has been closed.")
                    self.ledController.blinkFast()
                else:
                    print("Lid has been opened.")
                    self.killTests()
                    self.testsActivated = False
                    self.ledController.blink()

            time.sleep(0.1)

    def runTest(self):
        """
        Launch sub process for test runner script.
        """
        self.testsActivated = True
        self.session = subprocess.Popen(["sudo", "python3", TEST_RUNNER_PATH], preexec_fn=os.setsid)

    def killTests(self):
        """
        Terminate sub process for Test Runner if it exists. If that fails, kill it.

        Postcondition: self.session == None.
        """
        self.ledController.blink()
        if self.session is not None:
            print("ProggerStateManager: Terminating tests...")
            self.session.terminate()
            try:
                print("ProggerStateManager: Waiting for tests to terminate...")
                self.session.wait(3)
                print("ProggerStateManager: Tests have been Terminated.")
            except:
                print("ProggerStateManager: Forced to kill the tests....",  sys.exc_info()[0])
                traceback.print_exc()
                if self.session is not None:
                    self.session.kill()
                time.sleep(3)
            self.session = None

    def cleanup(self, source=None, frame=None):
        """
        Callback for SIGINT and SIGTERM signals.
        Kills tests, button watcher and led controller, then quit()s.
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