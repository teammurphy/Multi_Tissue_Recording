import ctypes

pulses = ctypes.CDLL("./pulse.so")

pulses.setup()
shouldbe90 = pulses.return90()
print(shouldbe90)
something = pulses.turnHigh()
print(something)
