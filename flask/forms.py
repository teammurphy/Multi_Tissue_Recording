from flask_wtf import FlaskForm
from wtforms import (BooleanField, DecimalField, FieldList, FileField,
                     FormField, HiddenField, IntegerField, SelectField,
                     SelectMultipleField, StringField, SubmitField, validators,
                     widgets)
from wtforms.fields.html5 import DateField


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class Tissue_Samples(FlaskForm):
    post_in_use = BooleanField(
        'Check If Post In Use')
    tissue_num = StringField('Tissue Number')
    type_of_tissue = StringField('Type of Tissue')


class upload_to_b_form(FlaskForm):
    date_recorded = DateField('Date Recorded', [validators.Required()])
    post = FieldList(FormField(Tissue_Samples), min_entries=6)
    frequency = DecimalField('Enter the Frequency')
    bio_reactor_num = IntegerField('Enter Bio Reactor Number')
    experiment_num = IntegerField('Enter Experiment number')
    vid_length = IntegerField('Enter the length of recording')
    submit = SubmitField('Submit')


class PickVid(FlaskForm):
    form_name = HiddenField('Form Name')
    experiment = SelectField('Experiment', id='select_experiment')
    date = SelectField('Date', id='select_date')
    vids = SelectField('Vids', id='select_vids')
    submit = SubmitField('Select Video')
