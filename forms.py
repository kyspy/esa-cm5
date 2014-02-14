from flask.ext.wtf import Form
from wtforms import FloatField, DateField, StringField, IntegerField, TextField, PasswordField, FileField, validators
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Area, Shift, Material, Location

def getAllAreas():
    return Area.query

def getAllLocations():
    return Location.query

def getAllShifts():
    return Shift.query

def getAllMaterials():
    return Material.query

class TrackingForm(Form):
    date = DateField('Date (MM/DD/YYYY)', validators=[Required()], format='%m/%d/%Y')
    station_start = FloatField('Starting Station (XX.XX)', validators = [Required()])
    station_end = FloatField('Ending Station (XX.XX)', validators = [Required()])
    quantity = FloatField('Quantity', validators = [Required()])
    area = QuerySelectField(query_factory=getAllAreas, get_label='area')
    location = QuerySelectField(query_factory=getAllLocations, get_label='location')
    shift = QuerySelectField(query_factory=getAllShifts, get_label='shift')
    material = QuerySelectField(query_factory=getAllMaterials, get_label='material')
    laborer = IntegerField('Laborer')
    foreman = IntegerField('Foreman')
    supervisor = IntegerField('Supervisor')

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

