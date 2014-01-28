from cm5_app import db

class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key = True)
    area = db.Column(db.String(3))
    location = db.Column(db.String(3))

    def __init__(self, area, location):
        self.area = area
        self.location = location

    def __repr__(self):
        return '<Area %r>' % self.area

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    date = db.Column(db.Date)
    station_start = db.Column(db.Float)
    station_end = db.Column(db.Float)
    quantity = db.Column(db.Float)

    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    area = db.relationship('Area', backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, timestamp, date, station_start, station_end, quantity, area):
        self.timestamp = timestamp
        self.date = date
        self.station_start = station_start
        self.station_end = station_end
        self.quantity = quantity
        self.area = area

    def __repr__(self):
        return '<Tracking %r>' % self.date

