import time
import threading
import RPi.GPIO as GPIO

step_pin = 16
dir_pin = 20
sleep_time = .001
GPIO.setmode(GPIO.BCM)
GPIO.setup(step_pin, GPIO.OUT)
GPIO.setup(dir_pin, GPIO.OUT)

light_pin = 17
GPIO.setup(light_pin, GPIO.OUT)

pos_pin = 21
neg_pin = 12
pulse_dur = 1
delay = .001
GPIO.setup(pos_pin, GPIO.OUT)
GPIO.setup(neg_pin, GPIO.OUT)


def rotate(num_steps, direction):
	if direction == 1:
		GPIO.output(dir_pin, GPIO.HIGH)
	else:
		GPIO.output(dir_pin, GPIO.LOW)

	count = 0
	while count < num_steps:
		GPIO.output(step_pin, GPIO.HIGH)
		time.sleep(sleep_time)
		GPIO.output(step_pin, GPIO.LOW)
		time.sleep(sleep_time)
		count += 1


def light(on):
	if on:
		GPIO.output(light_pin, GPIO.HIGH)
	else:
		GPIO.output(light_pin, GPIO.LOW)


def pulse(frequency):
	period = 1/frequency
	zero_v_time = period - 2*pulse_dur
	print(zero_v_time)
	thread = threading.current_thread()
	while getattr(thread, 'continues', True):
		print('Running')
		GPIO.output(pos_pin, GPIO.HIGH)
		time.sleep(pulse_dur)
		GPIO.output(pos_pin, GPIO.LOW)
		time.sleep(delay)
		GPIO.output(neg_pin, GPIO.HIGH)
		time.sleep(pulse_dur)
		GPIO.output(neg_pin, GPIO.LOW)
		time.sleep(zero_v_time)


def cleanup():
	light(False)
	GPIO.cleanup()
