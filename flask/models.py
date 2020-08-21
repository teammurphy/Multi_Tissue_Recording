import logging
import os
import shutil
import xml.etree.ElementTree as et
from dataclasses import asdict, dataclass
from datetime import datetime

from pytz import timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

tz = timezone('EST')
# TODO: need to do more robust test to esure realtionships are working but appears to be
# TODO: ensure adding process works
# TODO: what hnappens when get fails check that work flow

current_directory = os.getcwd()

UPLOAD_FOLDER = "static/uploads"
ZIPS_FOLDER = os.path.join(UPLOAD_FOLDER, 'zips')
UNPACKED_FOLDER = os.path.join(ZIPS_FOLDER, 'unpacked')
IMG_FOLDER = os.path.join(current_directory, 'static/img')


@ dataclass
class Experiment(db.Model):
    experiment_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    experiment_num: str = db.Column(
        db.String(120), nullable=False, unique=True)
    vids = db.relationship(
        'Video', back_populates='experiment', passive_deletes=True)


@ dataclass
class Video(db.Model):
    video_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    # TODO: add call factor float
    date_uploaded: datetime.date = db.Column(db.Date, nullable=False,
                                             default=datetime.now(tz))
    date_recorded: datetime.date = db.Column(db.Date, nullable=False)

    frequency: float = db.Column(db.Float, nullable=False)

    save_location: str = db.Column(db.String(120), nullable=False)

    bio_reactor_number: int = db.Column(db.Integer, nullable=True)

    # calibration distance is the user inputed length in mm of marker used to calibrate
    calibration_distance: float = db.Column(db.Float, nullable=True)

    # calibration factor is the calibration distance / length if the drawn calibration line in pixels
    calibration_factor: float = db.Column(db.Float, nullable=True)

    experiment_num: str = db.Column(db.String(120), db.ForeignKey(
        'experiment.experiment_num', ondelete='CASCADE'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='vids')

    bio_reactor_id: int = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.bio_reactor_id', ondelete='CASCADE'), nullable=True)
    bio_reactor = db.relationship(
        'Bio_reactor', back_populates='vids')

    tissues = db.relationship(
        'Tissue', back_populates='video', passive_deletes=True)


@ dataclass
class Tissue(db.Model):
    tissue_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    tissue_number: int = db.Column(db.Integer, nullable=False)
    tissue_type: str = db.Column(db.String(120), nullable=False)
    # REVIEW: maybe this should be a relationship
    post: int = db.Column(db.Integer, nullable=False)
    csv_path: str = db.Column(db.String(120), nullable=True)
    cross_section_dist: float = db.Column(db.Float, nullable=True)

    video_id: int = db.Column(
        db.Integer,  db.ForeignKey('video.video_id', ondelete='CASCADE'), nullable=False)
    video = db.relationship(
        'Video', back_populates='tissues')

    def __repr__(self):
        return '<Tissue %r>' % self.tissue_id


@ dataclass
class Bio_reactor(db.Model):
    bio_reactor_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    bio_reactor_number: int = db.Column(db.Integer, nullable=False)

    date_added: datetime.date = db.Column(db.Date, nullable=False)

    vids = db.relationship(
        'Video', back_populates='bio_reactor', passive_deletes=True)

    posts = db.relationship(
        'Post', back_populates='bio_reactor', passive_deletes=True)


@ dataclass
class Post(db.Model):
    post_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    post_number: int = db.Column(db.Integer, nullable=False)

    left_post_height: float = db.Column(db.Float, nullable=False)
    left_tissue_height: float = db.Column(db.Float, nullable=False)
    right_post_height: float = db.Column(db.Float, nullable=False)
    right_tissue_height: float = db.Column(db.Float, nullable=False)

    bio_reactor_id: int = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.bio_reactor_id', ondelete='CASCADE'), nullable=False)
    bio_reactor = db.relationship('Bio_reactor', back_populates='posts')


def delete_empties():
    for (root, dirs, files) in os.walk('static/uploads', topdown=False):
        if root == 'static/uploads/':
            break
        if not os.listdir(root):
            logging.info(root)
            os.rmdir(root)


def check_path_exisits(file_path_passed):
    if not os.path.exists(file_path_passed):
        os.makedirs(file_path_passed)


def populate():
    x = datetime(2020, 5, 17)

    insert_bio_reactor(1, x)
    insert_post(0, 3, 2.8, 3, 2.8, 1)
    insert_post(1, 3, 2.8, 3, 2.8, 1)
    insert_post(2, 3, 2.8, 3, 2.8, 1)
    insert_post(3, 3, 2.8, 3, 2.8, 1)
    insert_post(4, 3, 2.8, 3, 2.8, 1)
    insert_post(5, 3, 2.8, 3, 2.8, 1)


def insert_experiment(num_passed):
    if (db.session.query(Experiment.experiment_num).filter_by(experiment_num=num_passed).scalar() is None):
        new_expirment = Experiment(experiment_num=num_passed)
        db.session.add(new_expirment)
        db.session.commit()
    else:
        logging.info('already exists')


def insert_video(date_recorded_passed, experiment_num_passed, bio_reactor_id_passed, frequency_passed, save_path_passed, bio_reactor_num_passed):

    new_video = Video(date_recorded=date_recorded_passed,
                      experiment_num=experiment_num_passed,
                      bio_reactor_id=bio_reactor_id_passed,
                      frequency=frequency_passed, save_location=save_path_passed, bio_reactor_number=bio_reactor_num_passed)
    new_video.expirment = get_experiment_by_num(experiment_num_passed)
    new_video.bio_reactor = get_bio_reactor_by_id(bio_reactor_id_passed)

    db.session.add(new_video)
    db.session.commit()
    return new_video.video_id


def insert_tissue_sample(tissue_number_passed, tissue_type_passed, post_passed, video_id_passed):
    new_tissue = Tissue(
        tissue_number=tissue_number_passed, tissue_type=tissue_type_passed, post=post_passed, video_id=video_id_passed)
    new_tissue.video = get_video(video_id_passed)
    db.session.add(new_tissue)
    db.session.commit()


def insert_tissue_sample_csv(tissue_number_passed, tissue_type_passed, post_passed, video_id_passed, csv_passed):
    new_tissue = Tissue(
        tissue_number=tissue_number_passed, tissue_type=tissue_type_passed, post=post_passed, video_id=video_id_passed, csv_path=csv_passed)
    new_tissue.video = get_video(video_id_passed)
    db.session.add(new_tissue)
    db.session.commit()


def insert_bio_reactor(num_passed, date_added_passed):
    # TODO: if number is the same add with diffrent id and date

    bio_reactor_id = -1

    if (db.session.query(Bio_reactor.bio_reactor_id).filter_by(bio_reactor_number=num_passed, date_added=date_added_passed).scalar() is None):
        new_bio_reactor = Bio_reactor(
            bio_reactor_number=num_passed, date_added=date_added_passed)
        db.session.add(new_bio_reactor)
        db.session.commit()
        bio_reactor_id = new_bio_reactor.bio_reactor_id
    else:
        logging.info('already exists')
        # TODO: if date and num already exist ask uset to overwrite ??
        bio_reactor = Bio_reactor.query.filter_by(
            bio_reactor_number=num_passed, date_added=date_added_passed).first()
        bio_reactor_id = bio_reactor.bio_reactor_id

    return bio_reactor_id


def insert_post(post_number_passed, left_post_height_passed, left_tissue_height_passed, right_post_height_passed, right_tissue_height_passed, bio_reactor_id_passed):
    if (db.session.query(Post.post_id).filter_by(post_number=post_number_passed, bio_reactor_id=bio_reactor_id_passed).scalar() is None):
        new_post = Post(post_number=post_number_passed, left_post_height=left_post_height_passed, left_tissue_height=left_tissue_height_passed,
                        right_post_height=right_post_height_passed, right_tissue_height=right_tissue_height_passed, bio_reactor_id=bio_reactor_id_passed)
        db.session.add(new_post)
        db.session.commit()
    else:
        logging.info('already exists')

    # TODO: add error handling for all get functions


def check_vid_id(id_passed):
    # retuens true if the id exists
    if (db.session.query(Video.video_id).filter_by(video_id=id_passed).scalar() is None):
        return False
    else:
        return True


def check_tissue_id(id_passed):
    # retuens true if the id exists
    if (db.session.query(Tissue.tissue_id).filter_by(tissue_id=id_passed).scalar() is None):
        return False
    else:
        return True


def check_bio_id(id_passed):
    if (db.session.query(Bio_reactor.bio_reactor_id).filter_by(bio_reactor_id=id_passed).scalar() is None):
        return False
    else:
        return True


def get_bio_reactor_by_num(bio_reactor_num_passed):
    bio_reactor = Bio_reactor.query.filter_by(
        bio_reactor_number=bio_reactor_num_passed).first()
    return bio_reactor


def get_experiment_by_id(experiment_id_passed):
    expirment = Experiment.query.filter_by(
        experiment_id=experiment_id_passed).first()
    return expirment


def get_experiment_by_num(experiment_num_passed):
    expirment = Experiment.query.filter_by(
        experiment_num=experiment_num_passed).first()
    return expirment


def get_bio_reactor_by_id(bio_reactor_id_passed):
    bio_reactor = Bio_reactor.query.filter_by(
        bio_reactor_id=bio_reactor_id_passed).first()
    return bio_reactor


def get_bio_reactor_number(bio_reactor_id_passed):
    bio_reactor = Bio_reactor.query.filter_by(
        bio_reactor_id=bio_reactor_id_passed).first()
    return bio_reactor.bio_reactor_number


def get_tissue_by_id(tissue_id_passed):
    # gets tissue by the tissue id
    tissue = Tissue.query.filter_by(tissue_id=tissue_id_passed).first()
    return tissue


def get_dates_list(experiment_num_passed):
    experiment = get_experiment_by_num(experiment_num_passed)
    videos_list = experiment.vids
    dates = []
    for video in videos_list:
        if video.date_recorded not in dates:
            dates.append(video.date_recorded)
    return dates


def get_tissue_by_csv(csv_filepath):
    # gets tissue by the tissue id
    logging.info('csvpath')
    logging.info(csv_filepath)
    tissue = db.session.query(Tissue).filter_by(csv_path=csv_filepath).first()
    logging.info(tissue)
    return tissue


def get_video(video_id_passed):
    video = Video.query.filter_by(video_id=video_id_passed).first()
    return video


def add_tissue_csv(id_passed, path_passed):
    tissue = get_tissue_by_id(id_passed)
    tissue.csv_path = path_passed
    db.session.commit()


def add_calibration_distance(id_passed, cal_dist):
    video = get_video(id_passed)
    video.calibration_distance = cal_dist
    db.session.commit()


def add_calibration_factor(id_passed, cal_factor):
    video = get_video(id_passed)
    video.calibration_factor = cal_factor
    db.session.commit()


def add_cross_sections(vid_id_passed, cross_dist_passed):
    '''
    this gets a list of the tissues attached to a vid
    and accept a list of cross_distances
    then uses the order of the tissues left to right and the passed list 0.. to match them
    '''
    video = get_video(vid_id_passed)
    tissues = video.tissues
    for i, tissue in enumerate(tissues):
        tissue.cross_section_dist = cross_dist_passed[i]
    db.session.commit()


def get_all_experiments():
    result = []
    all = db.session.query(Experiment).all()
    [result.append(asdict(row)) for row in all]
    return result


def get_all_videos():
    result = []
    all = db.session.query(Video).all()
    [result.append(asdict(row)) for row in all]
    return result


def get_all_tissues():
    result = []
    all = db.session.query(Tissue).all()
    [result.append(asdict(row)) for row in all]
    return result


def get_all_bio_reactors():
    result = []
    all = db.session.query(Bio_reactor).all()
    [result.append(asdict(row)) for row in all]
    return result


def get_bio_choices():
    result = []
    [result.append((bio['bio_reactor_id'], f"Bio_num: {bio['bio_reactor_number']} Date Updated: {bio['date_added']}"))
     for bio in get_all_bio_reactors()]

    logging.info(result)

    return result


def get_posts(bio_reactor_id):
    result = []
    bio_reactor = get_bio_reactor_by_id(bio_reactor_id)
    all = bio_reactor.posts
    [result.append(asdict(row)) for row in all]
    return result


def delete_tissue(tissue_id):
    logging.info(tissue_id)
    tissue = get_tissue_by_id(tissue_id)
    logging.info(tissue)
    logging.info(tissue.csv_path)

    file_path = tissue.csv_path
    if file_path is not None and os.path.exists(file_path):
        os.remove(tissue.csv_path)
        delete_empties()
    else:
        logging.warning('There was no CSV')

    db.session.delete(tissue)
    db.session.commit()


def delete_video(vid_id):
    vid = get_video(vid_id)
    file_location = vid.save_location
    if os.path.isfile(file_location):
        os.remove(file_location)
        delete_empties()
    else:
        logging.error('Failed to delete vid')
    db.session.delete(vid)
    db.session.commit()


def delete_expirement(exp_id):
    exp = get_experiment_by_id(exp_id)
    experiment_num = exp.experiment_num
    file_path = f'static/uploads/{experiment_num}'
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
    db.session.delete(exp)
    db.session.commit()


def delete_bio_reactor(bio_id):
    bio = get_bio_reactor_by_id(bio_id)
    db.session.delete(bio)
    db.session.commit()


def calculate_bio_id(bio_reactor_num_passed, date_passed):

    # TODO: add better error handling if bio doesnt exist

    bio_reactor = (db.session.query(Bio_reactor).filter(
        Bio_reactor.bio_reactor_number == bio_reactor_num_passed, Bio_reactor.date_added <= date_passed).order_by(Bio_reactor.date_added.desc())).first()

    return bio_reactor.bio_reactor_id


def bio_reactors_to_xml(experiment_num_passed, li_of_bio_ids):
    root = et.Element('bio_reactors')
    for bio_id in li_of_bio_ids:
        bio_reactor_elem = et.SubElement(root, 'bio_reactor')
        bio_reactor_elem.set('bio_reactor_id', str(bio_id))
        bio_reactor = get_bio_reactor_by_id(bio_id)

        dic = asdict(bio_reactor)
        for key, val in dic.items():
            child = et.Element(key)
            child.text = str(val)
            child.set('data_type', type(val).__name__)
            bio_reactor_elem.append(child)

        if (bio_reactor.posts):
            posts_elem = et.SubElement(bio_reactor_elem, 'posts')
            for post in bio_reactor.posts:
                post_elem = et.SubElement(posts_elem, 'post')
                post_dic = asdict(post)
                post_elem.set('post_num', str(post_dic['post_number']))
                for key, val in post_dic.items():
                    child = et.Element(key)
                    child.text = str(val)
                    child.set('data_type', type(val).__name__)
                    post_elem.append(child)

    tree = et.ElementTree(root)
    with open(f'static/uploads/{experiment_num_passed}/bio_reactor_exp_num_{experiment_num_passed}.xml', 'wb') as f:
        tree.write(f)


def move_from_unpacked_to_exp(file_path_passed):
    '''
    gets the file path from the experement folder onward onstead of old from static
    realtes it to the file witin the unpacked fold
    then moved the file to the full file path
    '''

    splited_path = file_path_passed.split('/')
    from_exp = os.path.join(*splited_path[-4:])

    actual_file_path = os.path.join(UNPACKED_FOLDER, from_exp)
    check_path_exisits(os.path.split(file_path_passed)[0])
    if os.path.isfile(file_path_passed):
        logging.info('file already there')
    else:
        shutil.move(actual_file_path, file_path_passed)


def xml_to_bio(file_path):

    tree = et.parse(file_path)
    root = tree.getroot()

    for bio in root.iter('bio_reactor'):
        bio_dic = {}
        for elem in bio:
            if elem.tag != 'posts':
                elem_attrib = elem.attrib['data_type']
                if elem_attrib == 'int':
                    bio_dic.update({elem.tag: int(elem.text)})
                elif elem_attrib == 'float':
                    bio_dic.update({elem.tag: float(elem.text)})
                else:
                    bio_dic.update({elem.tag: elem.text})
        if check_bio_id(bio_dic['bio_reactor_id']) == False:
            bio_id = insert_bio_reactor(bio_dic['bio_reactor_number'], datetime.strptime(
                bio_dic['date_added'], "%Y-%m-%d"))
            for post in bio.iter('post'):
                post_dic = {}
                for elem in post:
                    elem_attrib = elem.attrib['data_type']
                    if elem_attrib == 'int':
                        post_dic.update({elem.tag: int(elem.text)})
                    elif elem_attrib == 'float':
                        post_dic.update({elem.tag: float(elem.text)})
                    else:
                        post_dic.update({elem.tag: elem.text})
                insert_post(post_dic['post_number'], post_dic['left_post_height'], post_dic['left_tissue_height'],
                            post_dic['right_post_height'], post_dic['right_tissue_height'], bio_id)

        else:
            logging.info("bio already exisits")
            bio_id = bio_dic['bio_reactor_id']


def xml_to_experiment(file_path):

    tree = et.parse(file_path)
    root = tree.getroot()

    exp_num = root.attrib['experiment_num']

    insert_experiment(exp_num)

    for video in root.iter('video'):
        vid_dic = {}
        for elem in video:
            if elem.tag != 'tissues':
                elem_attrib = elem.attrib['data_type']
                if elem_attrib == 'int':
                    vid_dic.update({elem.tag: int(elem.text)})
                elif elem_attrib == 'float':
                    vid_dic.update({elem.tag: float(elem.text)})
                elif elem_attrib == 'date':
                    vid_dic.update(
                        {elem.tag: datetime.strptime(elem.text, "%Y-%m-%d")})
                else:
                    vid_dic.update({elem.tag: elem.text})
        move_from_unpacked_to_exp(vid_dic['save_location'])

        if check_vid_id(vid_dic['video_id']) == False:
            # TODO: change bio id to new id
            vid_id = insert_video(vid_dic['date_recorded'], vid_dic['experiment_num'], vid_dic['bio_reactor_id'],
                                  vid_dic['frequency'], vid_dic['save_location'], vid_dic['bio_reactor_number'])
        else:
            logging.info('vid already in db')
            vid_id = vid_dic['video_id']

        for tissue in video.iter('tissue'):
            tissue_dic = {}
            for elem in tissue:
                elem_attrib = elem.attrib['data_type']
                if elem_attrib == 'int':
                    tissue_dic.update({elem.tag: int(elem.text)})
                elif elem_attrib == 'float':
                    tissue_dic.update({elem.tag: float(elem.text)})
                else:
                    tissue_dic.update({elem.tag: elem.text})
            if tissue_dic['csv_path'] != 'None':
                move_from_unpacked_to_exp(tissue_dic['csv_path'])

            # this used the id of the vid added above and not the orginal vid_id
            # insert_tissue_sample_csv(tissue_number_passed, tissue_type_passed, post_passed, video_id_passed, csv_passed):
            if check_tissue_id(tissue_dic['tissue_id']) == False:
                insert_tissue_sample_csv(
                    tissue_dic['tissue_number'], tissue_dic['tissue_type'], tissue_dic['post'], vid_id, tissue_dic['csv_path'])
            else:
                logging.info('tissue already in DB')


def experment_to_xml(experiment_num):
    used_bios_ids = []
    experiment = get_experiment_by_num(experiment_num)
    elem = et.Element('experiment')
    elem.set('experiment_num', experiment_num)
    # REVIEW: this is kindia slow but works
    if (experiment.vids):
        videos_elemant = et.SubElement(elem, 'videos')
        for vid in experiment.vids:
            dic = asdict(vid)
            video_elemant = et.SubElement(videos_elemant, 'video')
            video_elemant.set('video_id', str(dic['video_id']))
            for key, val in dic.items():
                if key == 'bio_reactor_id' and val not in used_bios_ids:
                    used_bios_ids.append(val)
                child = et.Element(key)
                child.set('data_type', type(val).__name__)
                child.text = str(val)
                video_elemant.append(child)

            if (vid.tissues):
                tissues_elemant = et.SubElement(video_elemant, 'tissues')

                for tissue in vid.tissues:
                    tissue_dic = asdict(tissue)
                    tissue_elemant = et.SubElement(tissues_elemant, 'tissue')
                    tissue_elemant.set(
                        'tissue_num', str(tissue_dic['tissue_number']))
                    for key, val in tissue_dic.items():
                        child = et.Element(key)
                        child.text = str(val)
                        child.set('data_type', type(val).__name__)
                        tissue_elemant.append(child)

    bio_reactors_to_xml(experiment_num, used_bios_ids)

    tree = et.ElementTree(elem)
    with open(f'static/uploads/{experiment_num}/{experiment_num}.xml', 'wb') as f:
        tree.write(f)
