#!flask/bin/python

import os
import unittest
from datetime import datetime

from config import basedir
from cm5_app import app, db
from models import Track, Area

class TestCase(unittest.TestCase):
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
        t = Track(timestamp = datetime.utcnow(), date = datetime(1979, 02, 01), station_start = 12.3, station_end = 12.4, quantity = 15, area_id = 1)
        db.session.add(t)
        db.session.commit()
        t = Track(timestamp = datetime.utcnow(), date = datetime(1982, 12, 30), station_start = 15.8, station_end = 16, quantity = 2, area_id = 2)
        db.session.add(t)
        db.session.commit()

    def test_area(self):
        a = Area(area = 'FVD', location = 'MPS')
        db.session.add(a)
        db.session.commit()
        a = Area(area = 'HSM', location = 'DWG')
        db.session.add(a)
        db.session.commit()

if __name__ == '__main__':
    unittest.main()