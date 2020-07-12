import logging
from datetime import datetime

from pytz import timezone

from flask_sqlalchemy import SQLAlchemy

# from Multi_tissue_tracking
db = SQLAlchemy()

tz = timezone('EST')
# TODO: need to do more robust test to esure realtionships are working but appears to be
# TODO: ensure adding process works
# TODO: what hnappens when get fails check that work flow


class Experiment(db.Model):
    experiment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_num = db.Column(
        db.Integer, nullable=False, unique=True)
    tissues = db.relationship('Tissue', back_populates='experiment')
    vids = db.relationship('Video', back_populates='experiment')


class Video(db.Model):
    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # TODO: add call factor float
    date_uploaded = db.Column(db.Date, nullable=False,
                              default=datetime.now(tz))
    date_recorded = db.Column(db.Date, nullable=False)

    frequency = db.Column(db.Float, nullable=False)

    save_location = db.Column(db.String(120), nullable=False)

    experiment_num = db.Column(db.Integer, db.ForeignKey(
        'experiment.experiment_num'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='vids')

    bio_reactor_num = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.bio_reactor_num'), nullable=False)
    bio_reactor = db.relationship('Bio_reactor', back_populates='vids')

    tissues = db.relationship('Tissue', back_populates='video')


class Tissue(db.Model):
    # REVIEW: pk maybe should be combo between tissue number and expirment number
    tissue_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tissue_number = db.Column(db.Integer, nullable=False)
    tissue_type = db.Column(db.String(120), nullable=False)
    post = db.Column(db.Integer, nullable=False)
    csv_path = db.Column(db.String(120), nullable=True)

    experiment_num = db.Column(db.Integer, db.ForeignKey(
        'experiment.experiment_num'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='tissues')

    bio_reactor_num = db.Column(db.Integer,  db.ForeignKey(
        'bio_reactor.bio_reactor_num'), nullable=False)
    bio_reactor = db.relationship('Bio_reactor', back_populates='tissues')

    video_id = db.Column(
        db.Integer,  db.ForeignKey('video.video_id'), nullable=False)
    video = db.relationship('Video', back_populates='tissues')

    def __repr__(self):
        return '<Tissue %r>' % self.id

# TODO: video and csv separe or not


class Bio_reactor(db.Model):
    bio_reactor_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    bio_reactor_num = db.Column(db.Integer, unique=True, nullable=False)
    tissues = db.relationship('Tissue', back_populates='bio_reactor')
    vids = db.relationship('Video', back_populates='bio_reactor')
    # TODO:put actual stuff here

# TODO: what happens if already exsits?


def insert_experiment(num_passed):
    new_expirment = Experiment(experiment_num=num_passed)
    db.session.add(new_expirment)
    db.session.commit()


def insert_video(date_recorded_passed, experiment_num_passed, bio_reactor_num_passed, frequency_passed, save_path_passed):

    new_video = Video(date_recorded=date_recorded_passed,
                      experiment_num=experiment_num_passed, bio_reactor_num=bio_reactor_num_passed, frequency=frequency_passed, save_location=save_path_passed)
    new_video.expirment = get_experiment(experiment_num_passed)
    new_video.bio_reactor = get_bio_reactor(bio_reactor_num_passed)

    db.session.add(new_video)
    db.session.commit()
    return new_video.video_id


def insert_tissue_sample(tissue_number_passed, tissue_type_passed, experiment_num_passed, bio_reactor_num_passed, post_passed, video_id_passed):
    new_tissue = Tissue(
        tissue_number=tissue_number_passed, tissue_type=tissue_type_passed, post=post_passed, experiment_num=experiment_num_passed, video_id=video_id_passed, bio_reactor_num=bio_reactor_num_passed)
    new_tissue.experiment = get_experiment(experiment_num_passed)
    new_tissue.bio_reactor = get_bio_reactor(bio_reactor_num_passed)
    new_tissue.video = get_video(video_id_passed)
    db.session.add(new_tissue)
    db.session.commit()


def insert_tissue_sample_csv(tissue_number_passed, tissue_type_passed, experiment_num_passed, bio_reactor_num_passed, post_passed, video_id_passed, csv_passed):
    new_tissue = Tissue(
        tissue_number=tissue_number_passed, tissue_type=tissue_type_passed, post=post_passed, experiment_num=experiment_num_passed, video_id=video_id_passed, bio_reactor_num=bio_reactor_num_passed, csv_path=csv_passed)
    new_tissue.experiment = get_experiment(experiment_num_passed)
    new_tissue.bio_reactor = get_bio_reactor(bio_reactor_num_passed)
    new_tissue.video = get_video(video_id_passed)
    db.session.add(new_tissue)
    db.session.commit()


def insert_bio_reactor(num_passed):
    new_bio_reactor = Bio_reactor(bio_reactor_num=num_passed)
    db.session.add(new_bio_reactor)
    db.session.commit()

# TODO: add error handling for all get functions


def get_experiment(experiment_num_passed):
    expirment = Experiment.query.filter_by(
        experiment_num=experiment_num_passed).first()
    return expirment


def get_bio_reactor(bio_reactor_num_passed):
    bio_reactor = Bio_reactor.query.filter_by(
        bio_reactor_num=bio_reactor_num_passed).first()
    return bio_reactor


def get_tissue(tissue_id_passed):
    # gets tissue by the tissue id
    tissue = Tissue.query.filter_by(tissue_id=tissue_id_passed).first()
    return tissue


def get_dates_list(experiment_num_passed):
    experiment = get_experiment(experiment_num_passed)
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
    tissue = get_tissue(id_passed)
    tissue.csv_path = path_passed
    # insert_tissue_sample_csv(tissue.tissue_number, tissue.tissue_type, tissue.experiment_num, tissue.bio_reactor_num,
    #      tissue.post, tissue.video_id, path_passed)
    db.session.commit()
