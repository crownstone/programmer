import RPi.GPIO as GPIO


BOARD_TO_GPIO = {
    "LED":6
}

# map of gpio to pins
GPIO_TO_PIN = {
    6: 31,
}

# get array of pins
LED_PIN = GPIO_TO_PIN[BOARD_TO_GPIO["LED"]]


class LedDriver:
    def __init__(self):
        pass

    def start(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(LED_PIN, GPIO.OUT)

    def cleanup(self):
        GPIO.cleanup(GPIO_TO_PIN[BOARD_TO_GPIO["LED"]])


    def turnLedOn(self):
        try:
            GPIO.output(GPIO_TO_PIN[BOARD_TO_GPIO["LED"]], GPIO.LOW)
        except:
            print("ERROR: Could not turn on LED")
            quit()

    def turnLedOff(self):
        try:
            GPIO.output(GPIO_TO_PIN[BOARD_TO_GPIO["LED"]], GPIO.HIGH)
        except:
            print("ERROR: Could not turn off LED")
            quit()

    def setLED(self, state):
        if state == True or state == 1:
            self.turnLedOn()
        else:
            self.turnLedOff()









