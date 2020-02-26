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

if version == "3": #this is the custom plug progger at the office
    print("Getting pin layout V3")
    from lib.GpioMap.proggerV3 import p_DISPLAY_BOARD_OUTPUT_PINS, p_GPIO_TO_PIN, p_BOARD_TO_GPIO, p_LED_PIN, p_GET_LID_OPEN_FROM_GPIO, p_ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING
elif version == "2": # this is the builtin one progger at bart's desk
    print("Getting pin layout V2")
    from lib.GpioMap.proggerV2 import p_DISPLAY_BOARD_OUTPUT_PINS, p_GPIO_TO_PIN, p_BOARD_TO_GPIO, p_LED_PIN, p_GET_LID_OPEN_FROM_GPIO, p_ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING
else: # this is the builtin one progger in china
    print("Getting pin layout V1")
    from lib.GpioMap.proggerV1 import p_DISPLAY_BOARD_OUTPUT_PINS, p_GPIO_TO_PIN, p_BOARD_TO_GPIO, p_LED_PIN, p_GET_LID_OPEN_FROM_GPIO, p_ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING

DISPLAY_BOARD_OUTPUT_PINS = p_DISPLAY_BOARD_OUTPUT_PINS
GPIO_TO_PIN = p_GPIO_TO_PIN
BOARD_TO_GPIO = p_BOARD_TO_GPIO
LED_PIN = p_LED_PIN
GET_LID_OPEN_FROM_GPIO = p_GET_LID_OPEN_FROM_GPIO
ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING = p_ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING