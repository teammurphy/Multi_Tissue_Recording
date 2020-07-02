import os

from flask import Flask, render_template, request, redirect

from camera_control import camera as cam

# Arducam Documentation: https://github.com/ArduCAM/RaspberryPi

app: Flask = Flask(__name__)

temp_val = 512
date = None
bio = None


@app.route('/')
def index():
	global temp_val
	return render_template('index.html', temp=str(temp_val))


@app.route('/', methods=['POST'])
def index_post():
	global bio, date
	posts = request.form.getlist('posts')
	bio = request.form['bio']
	date = request.form['dater']
	return render_template("index.html", posts=posts)


@app.route('/feed')
def feed():
	return Response(cam.gen(cam.Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stageup')
def stage_up():
	return 'MOVE STAGE UP'


@app.route('/stagedown')
def stage_down():
	return 'MOVE STAGE DOWN'


@app.route('/focusup')
def focus_up():
	global temp_val
	if temp_val < 1000:
		temp_val += 10

	value = (temp_val << 4) & 0x3ff0
	dat1 = (value >> 8) & 0x3f
	dat2 = value & 0xf0
	os.system("i2cset -y 0 0x0c %d %d" % (dat1, dat2))
	return redirect('/')


@app.route('/focusdown')
def focus_down():
	global temp_val
	if (temp_val >= 12):
		temp_val -= 10

	value = (temp_val << 4) & 0x3ff0
	dat1 = (value >> 8) & 0x3f
	dat2 = value & 0xf0
	os.system("i2cset -y 0 0x0c %d %d" % (dat1, dat2))
	return redirect('/')


@app.route('/upload')
def upload():
	os.system(
		'scp ../videotrial.h264 root@134.122.113.166:../home/jupyter-jack/scratch/Videos/'
	)
	return render_template("index.html")


@app.route('/record')
def record():
	cam.Camera.rec(10, date, bio)
	return render_template("index.html")


if __name__ == '__main__':
	app.run(host='0.0.0.0', threaded=True)
