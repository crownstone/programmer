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

displayGpio = {
   "T":  True,
   "LT": True,
   "RT": True,
   "M":  True,
   "LB": True,
   "RB": True,
   "B":  True,
}

p_BOARD_TO_GPIO = {
    "T":  16,
    "LT": 20,
    "RT": 21,
    "M":  19,
    "LB": 13,
    "RB": 12,
    "B":  5,

    "BUTTON": 4,
    "LID": 24,
    "LED": 6,

    "INPUT_1": 22,
    "INPUT_2": 23,
}

# map of gpio to pins
p_GPIO_TO_PIN = {
    4: 7,
    5: 29,
    6: 31,
    12: 32,
    13: 33,
    16: 36,
    19: 35,
    20: 38,
    21: 40,
    24: 18,
}

# get array of pins
p_DISPLAY_BOARD_OUTPUT_PINS = []
for gpio in displayGpio:
    p_DISPLAY_BOARD_OUTPUT_PINS.append(p_GPIO_TO_PIN[displayGpio[gpio]])


# get array of pins
p_LED_PIN = p_GPIO_TO_PIN[p_BOARD_TO_GPIO["LED"]]

p_GET_LID_OPEN_FROM_GPIO = lambda x : x

p_ADDITIONAL_WAIT_AFTER_BOOT_BEFORE_DIMMING = 0.2
