from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

db.drop_all()
db.create_all()

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key = True)
    bimimg_filename = db.Column(db.String(200))
    siteimg_filename = db.Column(db.String(200))
    site_caption = db.Column(db.String(200))
    date = db.Column(db.Date)
    note = db.Column(db.String(500))
    summary = db.Column(db.String(500))

    def __init__(self, bimimg_filename, siteimg_filename, site_caption, date, note, summary):
        self.bimimg_filename = bimimg_filename
        self.siteimg_filename = siteimg_filename
        self.site_caption = site_caption
        self.date = date
        self.note = note
        self.summary = summary

class Bimimage(db.Model):
    __tablename__ = 'bimimage'
    id = db.Column(db.Integer, primary_key = True)
    img_filename = db.Column(db.String(60))
    report_date = db.Column(db.Date, unique=True)
    report_type = db.Column(db.String(60))

    def __init__(self, img_filename, report_date, report_type):
        self.img_filename = img_filename
        self.report_date = report_date
        self.report_type = report_type

class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key = True)
    area = db.Column(db.String(20), unique = True)
    tracks = db.relationship('Track', backref='area', lazy='dynamic')

    def __init__(self, area):
        self.area = area

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<Area %r>' % self.area

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key = True)
    location = db.Column(db.String(20), unique = True)
    tracks = db.relationship('Track', backref='location', lazy='dynamic')

    def __init__(self, location):
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
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
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

if __name__ == '__main__':
    manager.run()