import logging
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from pytz import timezone

db = SQLAlchemy()

tz = timezone('EST')
# TODO: need to do more robust test to esure realtionships are working but appears to be
# TODO: ensure adding process works
# TODO: what hnappens when get fails check that work flow


@dataclass
class Experiment(db.Model):
    experiment_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    experiment_num: str = db.Column(
        db.String(120), nullable=False, unique=True)
    vids = db.relationship(
        'Video', back_populates='experiment', passive_deletes=True)


@dataclass
class Video(db.Model):
    video_id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # TODO: add call factor float
    date_uploaded: datetime.date = db.Column(db.Date, nullable=False,
                                             default=datetime.now(tz))
    date_recorded: datetime.date = db.Column(db.Date, nullable=False)

    frequency: float = db.Column(db.Float, nullable=False)

    save_location: str = db.Column(db.String(120), nullable=False)

    # calibration distance is the user inputed length in mm of marker used to calibrate
    calibration_distance: float = db.Column(db.Float, nullable=True)

    # calibration factor is the calibration distance / length if the drawn calibration line in pixels
    calibration_factor: float = db.Column(db.Float, nullable=True)

    experiment_num: str = db.Column(db.String(120), db.ForeignKey(
        'experiment.experiment_num', ondelete='CASCADE'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='vids')

    bio_reactor_number: int = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.bio_reactor_number', ondelete='CASCADE'), nullable=False)
    bio_reactor = db.relationship(
        'Bio_reactor', back_populates='vids')

    tissues = db.relationship(
        'Tissue', back_populates='video', passive_deletes=True)


@dataclass
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


@dataclass
class Bio_reactor(db.Model):
    bio_reactor_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    bio_reactor_number: int = db.Column(
        db.Integer, unique=True, nullable=False)
    vids = db.relationship(
        'Video', back_populates='bio_reactor', passive_deletes=True)

    posts = db.relationship(
        'Post', back_populates='bio_reactor', passive_deletes=True)


@dataclass
class Post(db.Model):
    post_id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_number: int = db.Column(db.Integer, nullable=False)

    left_post_height: float = db.Column(db.Float, nullable=False)
    left_tissue_height: float = db.Column(db.Float, nullable=False)
    right_post_height: float = db.Column(db.Float, nullable=False)
    right_tissue_height: float = db.Column(db.Float, nullable=False)

    bio_reactor_number: int = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.bio_reactor_number', ondelete='CASCADE'), nullable=False)
    bio_reactor = db.relationship('Bio_reactor', back_populates='posts')


def delete_empties():
    for (root, dirs, files) in os.walk('static/uploads', topdown=False):
        if root == 'static/uploads/':
            break
        if not os.listdir(root):
            logging.info(root)
            os.rmdir(root)

# TODO: what happens if already exsits?


def populate():
    insert_bio_reactor(1)
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


def insert_video(date_recorded_passed, experiment_num_passed, bio_reactor_num_passed, frequency_passed, save_path_passed):

    new_video = Video(date_recorded=date_recorded_passed,
                      experiment_num=experiment_num_passed, bio_reactor_number=bio_reactor_num_passed, frequency=frequency_passed, save_location=save_path_passed)
    new_video.expirment = get_experiment_by_num(experiment_num_passed)
    new_video.bio_reactor = get_bio_reactor_by_num(bio_reactor_num_passed)

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


def insert_bio_reactor(num_passed):
    if (db.session.query(Bio_reactor.bio_reactor_number).filter_by(bio_reactor_number=num_passed).scalar() is None):
        new_bio_reactor = Bio_reactor(bio_reactor_number=num_passed)
        db.session.add(new_bio_reactor)
        db.session.commit()
    else:
        logging.info('already exists')


def insert_post(post_number_passed, left_post_height_passed, left_tissue_height_passed, right_post_height_passed, right_tissue_height_passed, bio_reactor_num_passed):
    if (db.session.query(Post.post_id).filter_by(post_number=post_number_passed, bio_reactor_number=bio_reactor_num_passed).scalar() is None):
        new_post = Post(post_number=post_number_passed, left_post_height=left_post_height_passed, left_tissue_height=left_tissue_height_passed,
                        right_post_height=right_post_height_passed, right_tissue_height=right_tissue_height_passed, bio_reactor_number=bio_reactor_num_passed)
        db.session.add(new_post)
        db.session.commit()
    else:
        logging.info('already exists')

    # TODO: add error handling for all get functions


def get_experiment_by_num(experiment_num_passed):
    expirment = Experiment.query.filter_by(
        experiment_num=experiment_num_passed).first()
    return expirment


def get_bio_reactor_by_num(bio_reactor_num_passed):
    bio_reactor = Bio_reactor.query.filter_by(
        bio_reactor_number=bio_reactor_num_passed).first()
    return bio_reactor


def get_experiment_by_id(experiment_id_passed):
    expirment = Experiment.query.filter_by(
        experiment_id=experiment_id_passed).first()
    return expirment


def get_bio_reactor_by_id(bio_reactor_id_passed):
    bio_reactor = Bio_reactor.query.filter_by(
        bio_reactor_id=bio_reactor_id_passed).first()
    return bio_reactor


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
