# Overview

## Hardware

- Testbed
- Raspberry Pi 3B+
  - Custom hat
- JLink Base
- Power resistor
- Power measurement PCB
- Relay
- 8 segment display
- Button
- LED

## Software

The Raspberry Pi runs in read only mode, by using ramfs. This means that nothing is written to the SD card, so that it will not corrupt.

To prepare a new Raspberry Pi, follow [these instructions](../_system_scripts/README.md).

Now, the only code on the Raspberry Pi is:
- `watcherStart.sh`: Started by the service, and simply runs `UsbWatcher.py`.
- `UsbWatcher.py`: Checks if a USB drive is plugged in, and if so, runs the file defined by `config.py` as `STATE_MANAGER_PATH`.
- `config.py`: Contains paths of files and dirs.

Most of the code, is located on the USB drive. The most important:
- `ProggerStateManager.py`: Checks the lid and button, controls the status LED of the progger, and runs the `TestRunner.py`.
- `TestRunner.py`: Contains the code that actually performs the flashing and testing.

---
title: Programmer subprocesses (assuming all steps succeed)
---
sequenceDiagram
    UsbWatcher.py-->>+ProggerStateManager.py: onProgrammerDongleConnect
    ProggerStateManager.py->>ProggerStateManager.py: run()<br> checks button & lid
    ProggerStateManager.py-->>+TestRunner.py: onButtonPressed<br>runTest()
    TestRunner.py-->>+JLinkExe: program device
    JLinkExe-->>-TestRunner.py: return status
    TestRunner.py->>TestRunner.py: run tests
    TestRunner.py-->>ProggerStateManager.py: possibly fail
    TestRunner.py-->>+JLinkExe: reprogram device
    JLinkExe-->>-TestRunner.py: return status
    TestRunner.py-->>ProggerStateManager.py: onLidOpened<br>killTests()
    TestRunner.py-->>-ProggerStateManager.py: return success
    TestRunner.py-->>ProggerStateManager.py: onLidOpened, e.g. replace crownstone<br>killTests()
    ProggerStateManager.py-->>-UsbWatcher.py: onProgrammerDongleDisConnect

The `run test`
