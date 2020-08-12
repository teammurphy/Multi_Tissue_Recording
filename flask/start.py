import os
import subprocess
import threading

from flask import Flask, render_template, redirect

app = Flask(__name__)


@app.route('/')
def main():
	return render_template('start.html')


@app.route('/startup', methods=['POST'])
def startup():
	host = subprocess.Popen('hostname -I', universal_newlines=True, shell=True, stdout=subprocess.PIPE)
	host_name = host.stdout.read().rstrip()
	host.wait()
	thread = threading.Thread(target=launch_app)
	thread.start()
	return redirect(f'http://{host_name}:5000')


def launch_app():
	os.system('sudo python3 /root/Multi_Tissue_Recording/flask/app.py')


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
