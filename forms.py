from flask.ext.wtf import Form
from wtforms import FloatField, DateField
from wtforms.validators import Required

class TrackingForm(Form):
    date = DateField('Date (MM/DD/YYY):', validators=[Required()], format='%m/%d/%Y')
    station_start = FloatField('Starting Station:', validators = [Required()])
    station_end = FloatField('Ending Station:', validators = [Required()])
    quantity = FloatField('Quantity:', validators = [Required()])
