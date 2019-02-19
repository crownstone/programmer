from config import FW_SCRIPT_PATH


def findUsbBleDongleHciIndex():
    import subprocess
    from subprocess import Popen, PIPE

    session = subprocess.Popen(['hciconfig'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = session.communicate()
    session.terminate()

    hciInfoArray = str(stdout).split("hci")
    hciInfoArray.pop(0)

    usbIndex = 0

    for device in hciInfoArray:
        if "USB" in device:
            break
        usbIndex += 1

    return usbIndex


def programCrownstone():
    import subprocess
    from subprocess import Popen, PIPE

    session = subprocess.Popen(['JLinkExe', '-ExitonError', '1', FW_SCRIPT_PATH + 'full.script'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = session.communicate()

    vRef = None
    stringifiedResponse = stdout.decode("utf-8")
    if len(stringifiedResponse) > 0:
        responseArray = stringifiedResponse.split("VTref=")
        if len(responseArray) > 1:
            if len(responseArray[1]) > 5:
                vRef = float(responseArray[1][0:5])

    return (session.returncode, vRef)

