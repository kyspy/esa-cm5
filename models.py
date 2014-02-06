from cm5_app import db

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

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
