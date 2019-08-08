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
    "T": 24,
    "RT": 23,
    "LT": 25,
    "M": 26,
    "RB": 20,
    "LB": 22,
    "B": 21,

    "BUTTON": 4,
    "LID": 5,
    "LED": 18,

    "INPUT_1": 6,
    "INPUT_2": 17,
}


# map of gpio to pins
p_GPIO_TO_PIN = {
    4:  7,
    5:  29,
    6:  31,
    7:  26,
    10: 19,
    11: 23,
    12: 32,
    13: 33,
    16: 36,
    17: 11,
    18: 12,
    19: 35,
    20: 38,
    21: 40,
    22: 15,
    23: 16,
    24: 18,
    25: 22,
    26: 37,
}

# get array of pins
p_DISPLAY_BOARD_OUTPUT_PINS = []
for gpio in displayGpio:
    p_DISPLAY_BOARD_OUTPUT_PINS.append(p_GPIO_TO_PIN[p_BOARD_TO_GPIO[gpio]])

# get array of pins
p_LED_PIN = p_GPIO_TO_PIN[p_BOARD_TO_GPIO["LED"]]

p_GET_LID_OPEN_FROM_GPIO = lambda x : not x