from util import path
from lib.DisplayBoard.LoadingRunner import LoadingRunner
from lib.ButtonWatcher.ButtonWatcher import ButtonWatcher
from lib.DisplayBoard.DisplayDriver import DisplayDriver
from lib.DisplayBoard.LedController import LedController
import time

d = DisplayDriver()
l = LoadingRunner()
# buttonWatcher = ButtonWatcher()
ledController = LedController()
ledController.off()
# buttonWatcher.start()
# ledController.startBlinking()

d.start()
d.clearDisplay()

l.start()



# ar = ["B","LB","RB","M","LT","RT","T"]
#
# while True:
#     for x in ar:
#         print("showing", x)
#         d.illuminateSlot([x])
#         time.sleep(0.75)
#     d.clearDisplay()
