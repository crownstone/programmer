from BluenetLib.lib.core.uart.uartPackets.CurrentSamplesPacket import CurrentSamplesPacket

class VoltageSamplesPacket(CurrentSamplesPacket):
	def __init__(self, payload):
		super().__init__(payload)
		self.type = 'voltage'
