from cm5_app import db
from models import Bimimage

def ClearData():
    Bimimage.query.delete()

ClearData()

