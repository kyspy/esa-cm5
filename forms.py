from flask.ext.wtf import Form
from wtforms import FloatField, DateField, StringField, IntegerField, TextField, PasswordField, FileField, validators, TextAreaField
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Area, Shift, Material, Location, Report

def getAllAreas():
    return Area.query

def getAllLocations():
    return Location.query

def getAllShifts():
    return Shift.query

def getAllMaterials():
    return Material.query

def getAllReportDates():
    return Report.query.order_by(Report.id.desc())

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

class ReportForm(Form):
    bimimg = FileField('Tracking Image from BIM')
    siteimg = FileField('Progress Image from Site')
    summary = TextAreaField('Progress Summary')
    note = TextAreaField('Additional Notes')
    date = DateField('Date (MM/DD/YYYY)', validators=[Required()], format='%m/%d/%Y')
    site_caption = StringField('Progress Image Caption', validators = [Required()])
    edit_date = QuerySelectField(query_factory=getAllReportDates, get_label='date')

class AddAreaForm(Form):
    area = StringField('Area (for example East Cavern)', validators = [Required()])
    location = StringField('Location (for example East Wall)', validators = [Required()])

class AddShiftForm(Form):
    shift = StringField('Shift ID', validators = [Required()])
    start = IntegerField('Shift Start (for example 700)', validators = [Required()])
    end = IntegerField('Shift End (for example 1600)', validators = [Required()])

class AddMaterialForm(Form):
    material = StringField('Material (for example Geodrain)', validators = [Required()])
    unit =  StringField('Unit (for example Roll)', validators = [Required()])
