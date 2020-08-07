import time

import RPi.GPIO as GPIO

class motor_stepper:
	def __init__(self):
		self.step_pin = 16
		self.dir_pin = 20
		self.light_pin = 26
		self.sleep_time = .001

		self.pos_pin = 21
		self.neg_pin = 12
		self.pulse_dur = 5
		self.delay = .001

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.step_pin, GPIO.OUT)
		GPIO.setup(self.dir_pin, GPIO.OUT)
		GPIO.setup(self.light_pin, GPIO.OUT)

		GPIO.setup(self.pos_pin, GPIO.OUT)
		GPIO.setup(self.neg_pin, GPIO.OUT)

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

	def light(self, on):
		if on:
			GPIO.output(self.light_pin, GPIO.HIGH)
		else:
			GPIO.output(self.light_pin, GPIO.LOW)

	def pulse(self):
		GPIO.output(self.pos_pin, GPIO.HIGH)
		time.sleep(self.pulse_dur)
		GPIO.output(self.pos_pin, GPIO.LOW)
		time.sleep(self.delay)
		GPIO.output(self.neg_pin, GPIO.HIGH)
		time.sleep(self.pulse_dur)
		GPIO.output(self.neg_pin, GPIO.LOW)

	def cleanup(self):
		GPIO.output(self.light_pin, GPIO.LOW)
		GPIO.cleanup()



