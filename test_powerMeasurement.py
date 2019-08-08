import time
from util import path
from lib.PowerStateMeasurement.PowerStateMeasurement import PowerStateMeasurement

pw = PowerStateMeasurement()

pw.setup()

while True:
    pw.checkPowerStates()
    pw.powerThroughI1()
    pw.powerThroughI2()

    pw.powerThroughLoad()
    time.sleep(0.1)