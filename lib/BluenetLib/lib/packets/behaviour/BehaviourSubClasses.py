from BluenetLib.lib.util.Conversion import Conversion

from BluenetLib.lib.packets.behaviour.BehaviourTypes import BehaviourTimeType, BehaviourPresenceType
from BluenetLib.lib.util.DataStepper import DataStepper

class BehaviourTimeContainer:
    def __init__(self, fromTime, untilTime):
        self.fromTime  = fromTime
        self.untilTime = untilTime

class BehaviourTime:

    def __init__(self):
        self.timeType = None
        self.offset = 0
        self.valid = True

    def fromTime(self, hours, minutes):
        self.timeType = BehaviourTimeType.afterMidnight
        self.offset = 3600 * hours + 60 * minutes
        return self

    def fromType(self, timeType, offsetSeconds=0):
        self.timeType = timeType
        self.offset = offsetSeconds
        return self

    def fromData(self, data):
        if len(data) != 5:
            self.valid = False
            return self

        payload = DataStepper(data)

        firstByte = payload.getUInt8()
        if not BehaviourTimeType.has_value(firstByte):
            self.valid = False
            return self

        self.timeType = BehaviourTimeType(firstByte)
        self.offset = payload.getInt32()
        self.valid = True

        return self

    def getPacket(self):
        arr = []

        arr.append(self.timeType.value)
        arr += Conversion.int32_to_uint8_array(self.offset)

        return arr

    def getDictionary(self):
        returnDict = {}

        if self.timeType == BehaviourTimeType.afterSunset:
            returnDict["type"] = "SUNSET"
            returnDict["offsetMinutes"] = self.offset / 60
        elif self.timeType == BehaviourTimeType.afterSunrise:
            returnDict["type"] = "SUNRISE"
            returnDict["offsetMinutes"] = self.offset / 60
        else:
            returnDict["type"] = "CLOCK"
            returnDict["data"] = {"hours": (self.offset - self.offset % 3600) / 3600,
                                  "minutes": (self.offset % 3600) / 60}

        return returnDict

DEFAULT_PRESENCE_DELAY = 300 # seconds = 5 minutes
class BehaviourPresence:

    def __init__(self):
        self.presenceType = BehaviourPresenceType.ignorePresence
        self.locationIds = []
        self.delayInSeconds = 0
        self.valid = True

    def setSpherePresence(self, presenceType, delayInSeconds=DEFAULT_PRESENCE_DELAY):
        self.presenceType = presenceType
        self.delayInSeconds = delayInSeconds
        return self

    def setLocationPresence(self, presenceType, locationIds, delayInSeconds=DEFAULT_PRESENCE_DELAY):
        self.presenceType = presenceType
        self.locationIds = locationIds
        self.delayInSeconds = delayInSeconds
        return self

    def fromData(self, data):
        if len(data) != 13:
            self.valid = False
            return self

        payload = DataStepper(data)
        firstByte = payload.getUInt8()
        if not BehaviourPresenceType.has_value(firstByte):
            self.valid = False
            return self

        self.behaviourType = BehaviourPresenceType(firstByte)
        self.locationIds = self.unpackMask(payload.getUInt64())
        self.delayInSeconds = payload.getUInt32()

        return self

    def getMask(self, locationIds):
        result = 0
        bit = 1
        for locationId in locationIds:
            if locationId < 64:
                result = result | bit << locationId

        return result

    def unpackMask(self, mask):
        result = []
        bit = 1
        for i in range(0, 64):
            if (mask >> i & bit) == 1:
                result.append(i)

        return result

    def getPacket(self):
        arr = []

        arr.append(self.presenceType.value)
        arr += Conversion.uint64_to_uint8_array(self.getMask(self.locationIds))
        arr += Conversion.uint32_to_uint8_array(self.delayInSeconds)

        return arr

    def getDictionary(self):
        returnDict = {}

        if self.presenceType == BehaviourPresenceType.ignorePresence:
            returnDict["type"] = "IGNORE"

        elif self.presenceType == BehaviourPresenceType.somoneInLocation:
            returnDict["type"] = "SOMEBODY"
            returnDict["data"] = {"type": "LOCATION", "locationIds": self.locationIds}

        elif self.presenceType == BehaviourPresenceType.someoneInSphere:
            returnDict["type"] = "SOMEBODY"
            returnDict["data"] = {"type": "SPHERE"}

        elif self.presenceType == BehaviourPresenceType.nobodyInLocation:
            returnDict["type"] = "NOBODY"
            returnDict["data"] = {"type": "LOCATION", "locationIds": self.locationIds}

        elif self.presenceType == BehaviourPresenceType.nobodyInSphere:
            returnDict["type"] = "NOBODY"
            returnDict["data"] = {"type": "SPHERE"}

        if self.presenceType != BehaviourPresenceType.ignorePresence:
            returnDict["delay"] = self.delayInSeconds

        return returnDict


class ActiveDays:

    def __init__(self):
        self.Monday = True
        self.Tuesday = True
        self.Wednesday = True
        self.Thursday = True
        self.Friday = True
        self.Saturday = True
        self.Sunday = True

    def fromData(self, data):
        self.Sunday = (data >> 0) & 0x01 == 1
        self.Monday = (data >> 1) & 0x01 == 1
        self.Tuesday = (data >> 2) & 0x01 == 1
        self.Wednesday = (data >> 3) & 0x01 == 1
        self.Thursday = (data >> 4) & 0x01 == 1
        self.Friday = (data >> 5) & 0x01 == 1
        self.Saturday = (data >> 6) & 0x01 == 1
        return self

    def getMask(self):
        mask = 0

        # bits:
        MondayBit = 0
        TuesdayBit = 0
        WednesdayBit = 0
        ThursdayBit = 0
        FridayBit = 0
        SaturdayBit = 0
        SundayBit = 0
        if self.Sunday:  MondayBit = 1
        if self.Monday:  TuesdayBit = 1
        if self.Tuesday:  WednesdayBit = 1
        if self.Wednesday:  ThursdayBit = 1
        if self.Thursday:  FridayBit = 1
        if self.Friday:  SaturdayBit = 1
        if self.Saturday:  SundayBit = 1

        # configure mask
        mask = mask | SundayBit << 0
        mask = mask | MondayBit << 1
        mask = mask | TuesdayBit << 2
        mask = mask | WednesdayBit << 3
        mask = mask | ThursdayBit << 4
        mask = mask | FridayBit << 5
        mask = mask | SaturdayBit << 6

        return mask

    def getDictionary(self):
        returnDict = {
            "Sun": self.Sunday,
            "Mon": self.Monday,
            "Tue": self.Tuesday,
            "Wed": self.Wednesday,
            "Thu": self.Thursday,
            "Fri": self.Friday,
            "Sat": self.Saturday,
        }

        return returnDict
