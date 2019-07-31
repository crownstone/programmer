import RPi.GPIO as GPIO

from getPinLayout import LED_PIN


class LedDriver:
    def __init__(self):
        pass

    def start(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(LED_PIN, GPIO.OUT)

    def cleanup(self):
        GPIO.cleanup(LED_PIN)


    def turnLedOn(self):
        try:
            GPIO.output(LED_PIN, GPIO.LOW)
        except:
            print("ERROR: Could not turn on LED")
            quit()

    def turnLedOff(self):
        try:
            GPIO.output(LED_PIN, GPIO.HIGH)
        except:
            print("ERROR: Could not turn off LED")
            quit()

    def setLED(self, state):
        if state == True or state == 1:
            self.turnLedOn()
        else:
            self.turnLedOff()









