import time

import RPi.GPIO as GPIO

step_pin = 17
dir_pin = 27
sleep_time = .001
GPIO.setmode(GPIO.BCM)
GPIO.setup(step_pin, GPIO.OUT)
GPIO.setup(dir_pin, GPIO.OUT)

# 200 steps in full step mode = full turn?

count = 0
while count < 300:
	GPIO.output(step_pin, GPIO.HIGH)
	time.sleep(sleep_time)
	GPIO.output(step_pin, GPIO.LOW)
	time.sleep(sleep_time)
	count += 1
	print(count)

GPIO.cleanup()
