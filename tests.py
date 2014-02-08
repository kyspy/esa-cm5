#!flask/bin/python

import os
import unittest
from datetime import datetime

from config import basedir
from cm5_app import app, db
from models import Track, Area, Material, Shift


class TestDatabase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_track(self):
        t = Track(timestamp = datetime.utcnow(),
        date = datetime(1979, 02, 01),
        station_start = 12.3,
        station_end = 12.4,
        quantity = 15,
        laborer = 8,
        foreman = 5,
        supervisor = 8)
        db.session.add(t)
        db.session.commit()
        t = Track(timestamp = datetime.utcnow(),
        date = datetime(1982, 12, 30),
        station_start = 15.8,
        station_end = 16,
        quantity = 2,
        laborer = 12,
        foreman = 7,
        supervisor = 0)
        db.session.add(t)
        db.session.commit()

    def test_area(self):
        a = Area(area = 'FVD', location = 'MPS')
        db.session.add(a)
        db.session.commit()
        a = Area(area = 'HSM', location = 'DWG')
        db.session.add(a)
        db.session.commit()

    def test_material(self):
        m = Material(material = 'FVD', unit = 'MPS')
        db.session.add(m)
        db.session.commit()
        m = Material(material = 'HSM', unit = 'DWG')
        db.session.add(m)
        db.session.commit()

    def test_shift(self):
        s = Shift(shift = 'D', start = 7, end = 10)
        db.session.add(s)
        db.session.commit()
        s = Shift(shift = 'B', start = 8, end = 9)
        db.session.add(s)
        db.session.commit()

    def test_database_links(self):
        a = Area(area = 'PDS', location = 'WED')
        s = Shift(shift = 'X', start = 7, end = 10)
        m = Material(material = 'DFW', unit = 'WDS')
        t = Track(timestamp = datetime.utcnow(),
        date = datetime(1982, 12, 30),
        station_start = 15.8,
        station_end = 16,
        quantity = 2,
        laborer = 12,
        foreman = 7,
        supervisor = 0)

        db.session.add(a)
        db.session.add(s)
        db.session.add(m)
        db.session.add(t)
        db.session.commit()

        a.tracks.append(t)
        s.tracks.append(t)
        m.tracks.append(t)
        db.session.commit()


if __name__ == '__main__':
    unittest.main()