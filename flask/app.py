import logging
import os

#import camera_control.camera_pi as cams
import forms
import models
#from camera_control.camera_pi import Camera
from flask import Flask, Response, redirect, render_template, request

logging.basicConfig(filename='app.log',
                    format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.warning("New Run Starts Here")


def create_app():
    # TODO: move to wsgi??
    app = Flask(__name__)
    #  REVIEW: : this needs to be changed
    app.secret_key = 'development key'

    return app


app = create_app()


temp_val = 512
date = None
bio = None


def get_post_info(wtforms_list):
    # from flask multi tissue tracking
    # converts the list of form data in list of number and type or empty if that post is not in use
    count = 0
    li = []
    for entry in wtforms_list:
        if entry.data['post_in_use'] is True:
            count = count + 1
            li.append(
                entry.data['tissue_num'] + "," + entry.data['type_of_tissue'])
        else:
            li.append("empty")
    return count, li


'''
@app.route('/')
def index():
    global temp_val
    form = forms.upload_to_b_form()

    return render_template('index.html', temp=str(temp_val), form=form)
'''


@app.route('/', methods=['GET', 'POST'])
def index_post():
    form = forms.upload_to_b_form()
    if request.method == 'POST':
        # TODO: add form validation
        # REVIEW: delete gloabl???
        global bio, date
        # is a list of info about tissue 'empty' if string not in use
        # 'tissue_number,tissue_type' if it is in use
        li_of_post_info = get_post_info(form.post.entries)
        logging.info(li_of_post_info)

        # REVIEW: ideally would like to make these drop downs for experminet and bio reactor

        # checks if experiment exsits if it does makes it
        experiment_num = form.experiment_num.data
        logging.info(experiment_num)
        if models.get_experiment(experiment_num) is None:
            models.insert_experiment(experiment_num)

            # checks if experiment exsits if it does makes it
        bio_reactor_num = form.bio_reactor_num.data
        logging.info(bio_reactor_num)
        if models.get_bio_reactor(bio_reactor_num) is None:
            models.insert_bio_reactor(bio_reactor_num)

        # add the tissues to the databse as children of the vid, experiment and bio reactor
        add_tissues(li_of_post_info, experiment_num,
                    bio_reactor_num, new_video_id)
    else:
        return render_template("index.html", form=form)


@app.route('/feed')
def feed():
    return Response(cams.gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stageup')
def stage_up():
    return redirect('/')


@app.route('/stagedown')
def stage_down():
    return redirect('/')


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


@app.route('/record')
def record():
    Camera.rec(10, date, bio)
    return redirect('/')


@app.route('/upload')
def upload():
    os.system(
        "scp ../videotrial.h264 root@134.122.113.166:../home/jupyter-jack/scratch/Videos"
    )
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
