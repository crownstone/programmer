from util import path
from lib.ButtonWatcher.ButtonWatcher import ButtonWatcher
import time

buttonWatcher = ButtonWatcher()
buttonWatcher.start()

while True:
    print(buttonWatcher.buttonState)
    time.sleep(0.1)


