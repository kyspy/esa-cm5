from flask.ext.wtf import Form
from wtforms import FloatField, DateField, StringField, IntegerField, TextField, PasswordField, validators
from wtforms.validators import Required
from cm5_app import db
from models import User

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

class LoginForm(Form):
    login = TextField('Login', validators = [Required()])
    password = PasswordField('Password', validators = [Required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()

class RegistrationForm(Form):
    login = TextField('Login Name', validators=[Required()])
    email = TextField('Email')
    password = PasswordField('Password', validators=[Required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')

