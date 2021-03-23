from config import FW_SCRIPT_PATH


def findUartAddress():
    import subprocess
    from subprocess import Popen, PIPE

    session = subprocess.Popen(['ls', "/dev"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = session.communicate()
    session.terminate()

    devList = stdout.decode("utf-8").split("\n")

    usbIndex = 0

    for device in devList:
        if "ACM" in device:
            return "/dev/" + device

    return False


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
            print(device)
            break
        usbIndex += 1

    return usbIndex

def findUsbBleDongleHciAddress():
    import subprocess
    from subprocess import Popen, PIPE
    import re
    regex = re.compile("Address: (.{17})")

    session = subprocess.Popen(['hciconfig'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = session.communicate()
    session.terminate()

    hciInfoArray = str(stdout).split("hci")
    hciInfoArray.pop(0)

    for device in hciInfoArray:
        if "USB" in device:
            return regex.findall(device)[0]


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


    if session.returncode != 0:
        print("FAILED TO PROGRAM", stdout)

    return (session.returncode, vRef)

