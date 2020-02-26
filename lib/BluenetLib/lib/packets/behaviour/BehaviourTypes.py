from enum import IntEnum

DAY_START_TIME_SECONDS_SINCE_MIDNIGHT = 4*3600

class BehaviourType(IntEnum):
    behaviour  = 0
    twilight   = 1
    smartTimer = 2

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class BehaviourTimeType(IntEnum):
    afterMidnight = 0
    afterSunrise  = 1
    afterSunset   = 2

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)



class BehaviourPresenceType(IntEnum):
    ignorePresence   = 0
    somoneInLocation = 1
    nobodyInLocation = 2
    someoneInSphere  = 3
    nobodyInSphere   = 4

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

