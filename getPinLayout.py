DISPLAY_BOARD_OUTPUT_PINS = None
GPIO_TO_PIN = None
BOARD_TO_GPIO = None
LED_PIN = None


GET_LID_OPEN_FROM_GPIO = None


version = "1"
try:
    handle = open("/home/pi/programmer_pin_version", "r")
    version = handle.read()
    handle.close()
except:
    pass

version = version.strip()

if version == "2":
    print("Getting pin layout V2")
    from lib.GpioMap.proggerV2 import p_DISPLAY_BOARD_OUTPUT_PINS, p_GPIO_TO_PIN, p_BOARD_TO_GPIO, p_LED_PIN, p_GET_LID_OPEN_FROM_GPIO
else:
    print("Getting pin layout V1")
    from lib.GpioMap.proggerV1 import p_DISPLAY_BOARD_OUTPUT_PINS, p_GPIO_TO_PIN, p_BOARD_TO_GPIO, p_LED_PIN, p_GET_LID_OPEN_FROM_GPIO

DISPLAY_BOARD_OUTPUT_PINS = p_DISPLAY_BOARD_OUTPUT_PINS
GPIO_TO_PIN = p_GPIO_TO_PIN
BOARD_TO_GPIO = p_BOARD_TO_GPIO
LED_PIN = p_LED_PIN
GET_LID_OPEN_FROM_GPIO = p_GET_LID_OPEN_FROM_GPIO
