from cm5_app import db
from flask_login import UserMixin

class Bimlink(db.Model):
    __tablename__ = 'bimlink'
    revit_id = db.Column(db.Integer, primary_key = True)
    excel_id = db.Column(db.String(60), unique=True)

    def __init__(self, revit_id, excel_id):
        self.revit_id = revit_id
        self.excel_id = excel_id

class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key = True)
    area = db.Column(db.String(20), unique=True)
    location = db.Column(db.String(20))
    tracks = db.relationship('Track', backref='area', lazy='dynamic')

    def __init__(self, area, location):
        self.area = area
        self.location = location

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<Area %r>' % self.area

class Shift(db.Model):
    __tablename__ = 'shift'
    id = db.Column(db.Integer, primary_key = True)
    shift = db.Column(db.String(1), unique=True)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    tracks = db.relationship('Track', backref='shift', lazy='dynamic')

    def __init__(self, shift, start, end):
        self.shift = shift
        self.start = start
        self.end = end

    def get_id(self):
        return unicode(self.id)

class Material(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key = True)
    material = db.Column(db.String(20), unique=True)
    unit = db.Column(db.String(20))
    tracks = db.relationship('Track', backref='material', lazy='dynamic')

    def __init__(self, material, unit):
        self.material = material
        self.unit = unit

    def get_id(self):
        return unicode(self.id)

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    date = db.Column(db.Date)
    station_start = db.Column(db.Float)
    station_end = db.Column(db.Float)
    quantity = db.Column(db.Float)
    laborer = db.Column(db.Integer)
    foreman = db.Column(db.Integer)
    supervisor = db.Column(db.Integer)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'))

    def __init__(self, timestamp, date, station_start, station_end, quantity, laborer, foreman, supervisor):
        self.timestamp = timestamp
        self.date = date
        self.station_start = station_start
        self.station_end = station_end
        self.quantity = quantity
        self.laborer = laborer
        self.foreman = foreman
        self.supervisor = supervisor

    def get_id(self):
        return unicode(self.id)

class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.password = password

    @staticmethod
    def get(email):
        for user in USERS:
            if user[0] == email:
                return User(user[0], user[1])
        return None

USERS = (("kfarrell@mtacc-esa.info", "Esalirovc123"),
          ("omoshkov@mtacc-esa.info", "Esalirovc1"),
          ("goldrunt@gmail.com", "goldrunt")
          )
