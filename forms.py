from flask.ext.wtf import Form
from wtforms import FloatField, DateField, StringField, IntegerField, TextField, PasswordField, FileField, validators
from wtforms.validators import Required

class TrackingForm(Form):
    date = DateField('Date (MM/DD/YYYY)', validators=[Required()], format='%m/%d/%Y')
    station_start = FloatField('Starting Station (XX.XX)', validators = [Required()])
    station_end = FloatField('Ending Station (XX.XX)', validators = [Required()])
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
    #look into SelectField for Shift and Area

class LoginForm(Form):
    email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])

class WeeklyImgForm(Form):
    img = FileField()
    date = DateField('Date of Report (MM/DD/YYYY)', validators=[Required()], format='%m/%d/%Y')

class WeeklyFieldImgForm(Form):
    img = FileField()
    date = DateField('Date of Report (MM/DD/YYYY)', validators=[Required()], format='%m/%d/%Y')
    caption = StringField('Caption', validators = [Required()])

class WeeklyForm(Form):
    summary = TextField('Progress Summary')
    note = TextField('Additional Notes')

