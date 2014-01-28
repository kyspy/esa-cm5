#!flask/bin/python
import os
import unittest
from datetime import datetime

from config import basedir
from esa_app import app, db, Tracking

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

    def test_tracking(self):
        t = Track(station_start = 12.3, station_end = 12.4, quantity = 15)
        db.session.add(t)
        db.session.commit()
        t = Track(station_start = 15.8, station_end = 16, quantity = 2)
        db.session.add(t)
        db.session.commit()

if __name__ == '__main__':
    unittest.main()