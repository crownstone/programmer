import asyncio

import RPi.GPIO as GPIO
import time,random


#                          -----------
#   display diagram:       |    T    |
#                       -- ----------- --
#                      |  |           |  |
#                      |LT|           |RT|
#                      |  |           |  |
#                       -- ----------- --
#                          |    M    |
#                       -- ----------- --
#                      |  |           |  |
#                      |LB|           |RB|
#                      |  |           |  |
#                       -- ----------- --
#                         |     B     |
#                          -----------

BOARD_TO_GPIO = {
    "T":  16,
    "LT": 20,
    "RT": 21,
    "M":  19,
    "LB": 13,
    "RB": 12,
    "B":  5,
}

# map of gpio to pins
GPIO_TO_PIN = {
    5: 29,
    12: 32,
    13: 33,
    16: 36,
    19: 35,
    20: 38,
    21: 40,
}

# get array of pins
DISPLAY_BOARD_OUTPUT_PINS = []
for gpio in GPIO_TO_PIN:
    DISPLAY_BOARD_OUTPUT_PINS.append(GPIO_TO_PIN[gpio])



class DisplayDriver:
    persistingSlots = [] # this lives through all instances of this class

    def __init__(self):
        pass

    def start(self):
        self.persistingSlots = []
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(DISPLAY_BOARD_OUTPUT_PINS, GPIO.OUT)

        self.clearDisplay(noPersistance=True)

    def cleanup(self):
        GPIO.cleanup(DISPLAY_BOARD_OUTPUT_PINS)

    def clearDisplay(self, noPersistance=False):
        GPIO.output(DISPLAY_BOARD_OUTPUT_PINS, GPIO.HIGH)
        if not noPersistance:
            self.illuminateSlot(self.persistingSlots)


    def persistSlot(self, slot):
        if slot in BOARD_TO_GPIO:
            if slot not in self.persistingSlots:
                self.persistingSlots.append(slot)

    def clearPersistedSlots(self):
        self.persistingSlots = []


    def setSymbol(self, symbol):
        self.clearDisplay(noPersistance=True)

        if symbol == 0 or symbol == '0':
            self.illuminateSlot(["T","LT","RT","B","RB","LB"])
        elif symbol == 1 or symbol == '1':
            self.illuminateSlot(["RT","RB"])
        elif symbol == 2 or symbol == '2':
            self.illuminateSlot(["T","RT","M","LB","B"])
        elif symbol == 3 or symbol == '3':
            self.illuminateSlot(["T","RT","M","RB","B"])
        elif symbol == 4 or symbol == '4':
            self.illuminateSlot(["LT","RT","M","RB"])
        elif symbol == 5 or symbol == '5':
            self.illuminateSlot(["T","LT","M","RB","B"])
        elif symbol == 6 or symbol == '6':
            self.illuminateSlot(["T","LT","M","LB","RB","B"])
        elif symbol == 7 or symbol == '7':
            self.illuminateSlot(["T","RT","RB"])
        elif symbol == 8 or symbol == '8':
            self.illuminateSlot(["T","LT","RT","M","LB","RB","B"])
        elif symbol == 9 or symbol == '9':
            self.illuminateSlot(["T","LT","RT","M","RB","B"])
        elif symbol == 'E' or symbol == 'e':
            self.illuminateSlot(["T", "LT", "M", "LB", "B"])
        elif symbol == 'D' or symbol == 'd':
            self.illuminateSlot(["RT", "M", "LB", "RB", "B"])
        elif symbol == 'B' or symbol == 'b':
            self.illuminateSlot(["LT", "M", "LB", "RB", "B"])
        elif symbol == 'O' or symbol == 'o':
            self.illuminateSlot(["T","LT","RT","B","RB","LB"])
        elif symbol == 'R' or symbol == 'r':
            self.illuminateSlot(["T","LT","RT","M","RB","LB"])
        elif symbol == 'S' or symbol == 's':
            self.illuminateSlot(["T","LT","M","RB","B"])
        elif symbol == 'U' or symbol == 'u':
            self.illuminateSlot(["LT", "RT", "LB", "RB", "B"])
        elif symbol == 'C' or symbol == 'c':
            self.illuminateSlot(["T", "LT", "LB", "B"])
        elif symbol == ' |':
            self.illuminateSlot(["RT", "RB"])
        elif symbol == '| ':
            self.illuminateSlot(["LT", "LB"])
        elif symbol == '| |':
            self.illuminateSlot(["LT", "LB", "RT", "RB"])
        elif symbol == '- |':
            self.illuminateSlot(["LB", "RT", "RB"])
        elif symbol == ' ^':
            self.illuminateSlot(["RT"])


    def illuminateSlot(self,slotArray):
        for slot in slotArray:
            GPIO.output(GPIO_TO_PIN[BOARD_TO_GPIO[slot]], GPIO.LOW)


    async def showBuildUp(self):
        delay = 0.1
        self.clearDisplay(noPersistance=True)

        self.illuminateSlot(["B"])
        await asyncio.sleep(delay)
        self.illuminateSlot(["RB"])
        await asyncio.sleep(delay)
        self.illuminateSlot(["LB"])
        await asyncio.sleep(delay)
        self.illuminateSlot(["M"])
        await asyncio.sleep(delay)
        self.illuminateSlot(["LT"])
        await asyncio.sleep(delay)
        self.illuminateSlot(["RT"])
        await asyncio.sleep(delay)
        self.illuminateSlot(["T"])
        await asyncio.sleep(delay)

        self.clearDisplay(noPersistance=True)









