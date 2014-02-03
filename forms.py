from flask.ext.wtf import Form
from wtforms import FloatField, DateField, StringField, IntegerField
from wtforms.validators import Required

class TrackingForm(Form):
    date = DateField('Date (MM/DD/YYYY)', validators=[Required()], format='%m/%d/%Y')
    station_start = FloatField('Starting Station', validators = [Required()])
    station_end = FloatField('Ending Station', validators = [Required()])
    quantity = FloatField('Quantity', validators = [Required()])
    area = StringField('Area', validators = [Required()])
    location = StringField('Location', validators = [Required()])
    shift = StringField('Shift', validators = [Required()])
    start = IntegerField('Shift Start', validators = [Required()])
    end = IntegerField('Shift End', validators = [Required()])
    material = StringField('Material', validators = [Required()])
    unit = StringField('Material Unit', validators = [Required()])
    laborer = IntegerField('Laborer')
    foreman = IntegerField('Foreman')
    supervisor = IntegerField('Supervisor')

