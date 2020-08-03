import time

import RPi.GPIO as GPIO

class motor_stepper:
	def __init__(self):
		self.step_pin = 17
		self.dir_pin = 27
		self.sleep_time = .001
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.step_pin, GPIO.OUT)
		GPIO.setup(self.dir_pin, GPIO.OUT)

	def rotate(self, num_steps, direction):
		if direction == 1:
			GPIO.output(self.dir_pin, GPIO.HIGH)
		else:
			GPIO.output(self.dir_pin, GPIO.LOW)

		count = 0
		while count < num_steps:
			GPIO.output(self.step_pin, GPIO.HIGH)
			time.sleep(self.sleep_time)
			GPIO.output(self.step_pin, GPIO.LOW)
			time.sleep(self.sleep_time)
			count += 1
		return

	def __del__(self):
		GPIO.cleanup()
