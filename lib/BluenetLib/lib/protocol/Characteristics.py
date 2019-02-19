class DeviceCharacteristics:
    HardwareRevision = "2a27"
    FirmwareRevision = "2a26"


class CrownstoneCharacteristics:
    Control          = "24f00001-7d10-4805-bfc1-7663a01c3bff"
    MeshControl      = "24f00002-7d10-4805-bfc1-7663a01c3bff"
    ConfigControl    = "24f00004-7d10-4805-bfc1-7663a01c3bff"
    ConfigRead       = "24f00005-7d10-4805-bfc1-7663a01c3bff"
    StateControl     = "24f00006-7d10-4805-bfc1-7663a01c3bff"
    StateRead        = "24f00007-7d10-4805-bfc1-7663a01c3bff"
    SessionNonce     = "24f00008-7d10-4805-bfc1-7663a01c3bff"
    FactoryReset     = "24f00009-7d10-4805-bfc1-7663a01c3bff"


class SetupCharacteristics:
    Control          = "24f10001-7d10-4805-bfc1-7663a01c3bff"
    MacAddress       = "24f10002-7d10-4805-bfc1-7663a01c3bff"
    SessionKey       = "24f10003-7d10-4805-bfc1-7663a01c3bff"
    ConfigControl    = "24f10004-7d10-4805-bfc1-7663a01c3bff"
    ConfigRead       = "24f10005-7d10-4805-bfc1-7663a01c3bff"
    GoToDFU          = "24f10006-7d10-4805-bfc1-7663a01c3bff"
    SetupControl     = "24f10007-7d10-4805-bfc1-7663a01c3bff"
    SessionNonce     = "24f10008-7d10-4805-bfc1-7663a01c3bff"



class GeneralCharacteristics:
    Temperature      = "24f20001-7d10-4805-bfc1-7663a01c3bff"
    Reset            = "24f20002-7d10-4805-bfc1-7663a01c3bff"


class PowerCharacteristics:
    PWM              = "24f30001-7d10-4805-bfc1-7663a01c3bff"
    Relay            = "24f30002-7d10-4805-bfc1-7663a01c3bff"
    PowerSamples     = "24f30003-7d10-4805-bfc1-7663a01c3bff"
    PowerConsumption = "24f30004-7d10-4805-bfc1-7663a01c3bff"


class IndoorLocalizationCharacteristics:
    TrackControl     = "24f40001-7d10-4805-bfc1-7663a01c3bff"
    TrackedDevices   = "24f40002-7d10-4805-bfc1-7663a01c3bff"
    ScanControl      = "24f40003-7d10-4805-bfc1-7663a01c3bff"
    ScannedDevices   = "24f40004-7d10-4805-bfc1-7663a01c3bff"
    RSSI             = "24f40005-7d10-4805-bfc1-7663a01c3bff"


class ScheduleCharacteristics:
    SetTime          = "24f50001-7d10-4805-bfc1-7663a01c3bff"
    ScheduleWrite    = "24f50002-7d10-4805-bfc1-7663a01c3bff"
    ScheduleRead     = "24f50003-7d10-4805-bfc1-7663a01c3bff"


class MeshCharacteristics:
    MeshData         = "2a1e0004-fd51-d882-8ba8-b98c0000cd1e"
    Value            = "2a1e0005-fd51-d882-8ba8-b98c0000cd1e"


class DFUCharacteristics:
    ControlPoint   = "00001531-1212-EFDE-1523-785FEABCD123"
    Packet         = "00001532-1212-EFDE-1523-785FEABCD123"

