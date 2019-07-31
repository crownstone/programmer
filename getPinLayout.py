import os


DISPLAY_BOARD_OUTPUT_PINS = None
GPIO_TO_PIN = None
BOARD_TO_GPIO = None
LED_PIN = None

if "PROGGER_PIN_LAYOUT_VERSION" in os.environ:
    if os.environ["PROGGER_PIN_LAYOUT_VERSION"]:
        print("Getting pinlayout V2")
        from lib.GpioMap.proggerV2 import p_DISPLAY_BOARD_OUTPUT_PINS, p_GPIO_TO_PIN, p_BOARD_TO_GPIO, p_LED_PIN
        DISPLAY_BOARD_OUTPUT_PINS = p_DISPLAY_BOARD_OUTPUT_PINS
        GPIO_TO_PIN = p_GPIO_TO_PIN
        BOARD_TO_GPIO = p_BOARD_TO_GPIO
        LED_PIN = p_LED_PIN
else:
    print("Getting pinlayout V1")
    from lib.GpioMap.proggerV1 import p_DISPLAY_BOARD_OUTPUT_PINS, p_GPIO_TO_PIN, p_BOARD_TO_GPIO, p_LED_PIN
    DISPLAY_BOARD_OUTPUT_PINS = p_DISPLAY_BOARD_OUTPUT_PINS
    GPIO_TO_PIN = p_GPIO_TO_PIN
    BOARD_TO_GPIO = p_BOARD_TO_GPIO
    LED_PIN = p_LED_PIN
