import logging
import os

import camera_control.camera_pi as cams
import forms
import models
from camera_control.camera_pi import Camera
from flask import Flask, Response, redirect, render_template, request

logging.basicConfig(filename='app.log',
                    format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.warning("New Run Starts Here")

ip_of_host = '159.89.84.193'

def create_app():
    # TODO: move to wsgi??
    app = Flask(__name__)
    # TODO: change this to where the databse is
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://newuser:newpassword@{ip_of_host}:3306/test_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Shows sql querys being made if having database issue set to true
    app.config['SQLALCHEMY_ECHO'] = False
    #  REVIEW: : this needs to be changed
    app.secret_key = 'development key'
    models.db.init_app(app)

    return app


app = create_app()


temp_val = 512

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


def add_tissues(li_of_post_info, experiment_num_passed, bio_reactor_num_passed, video_id_passed):
    # from flask multi tissue tracking
    for post, info in enumerate(li_of_post_info):

        '''
        enumerate and post is used beacuse the location on the item in the list
        if not 'empty' is the number of the post it is on whie info is the metadata about the tissue
        '''
        # check is there is a tissue on post
        if info != 'empty':
            logging.info(info)
            # splits so tissue num is in [0] and type in [1]
            split_list = info.split(',')
            tissue_num = split_list[0]
            tissue_type = split_list[1]
            models.insert_tissue_sample(
                tissue_num, tissue_type, post, video_id_passed)

@app.route('/ssh', methods=["GET", "POST"])
def ssh_path():
    global ip_of_host
    if request.method == "POST":
        ip_of_host = request.form.get("ip")
    return render_template('ssh.html', currssh = ip_of_host)

@app.route('/', methods=['GET', 'POST'])
def index_post():
    form = forms.upload_to_b_form()
    if request.method == 'POST':
        # TODO: add form validation
        '''
        is a list of info about tissue 'empty' if string not in use
        'tissue_number,tissue_type' if it is in use
        tup[0] is count of tissues tup[1] is list of tiisue infor
         '''
        tup = get_post_info(form.post.entries)
        li_of_post_info = tup[1]
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

        date_string = form.date_recorded.data.strftime('%m_%d_%Y')
        vid_name = date_string + "_" + "Freq" + str(form.frequency.data) + "_" + "Bio" + str(bio_reactor_num) + ".h264"
        path_to_file = f'static/uploads/{experiment_num}/{date_string}/videoFiles/{vid_name}'
        new_video_id = models.insert_video(form.date_recorded.data, experiment_num, bio_reactor_num, form.frequency.data, path_to_file)
        Camera.rec(10, path_to_file)
        # add the tissues to the databse as children of the vid, experiment and bio reactor
        add_tissues(li_of_post_info, experiment_num, bio_reactor_num, new_video_id)
        return'''
        <h1>check database</h1>
        '''

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


@app.route('/upload')
def upload():
    os.system(
        f'rsync -a --ignore-existing static/uploads/ {ip_of_host}:~/uploader/'
    )
	# "scp ../videotrial.h264 root@134.122.113.166:../home/jupyter-jack/scratch/Videos"
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
