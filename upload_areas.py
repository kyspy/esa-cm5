from cm5_app import db
from xlrd import open_workbook
from models import Area, Location


def UploadAreas():

    book = open_workbook('static/excel/areas.xls')
    sheet = book.sheet_by_index(0)

    for x in range(0, sheet.nrows):
        area= sheet.cell(x,0).value
        location= sheet.cell(x,1).value

        a = Area.query.filter_by(area = area).first()
        if a == None:
            a = Area(area = area)
            db.session.add(a)
            db.session.commit()

        l = Location.query.filter_by(location = location).first()
        if l == None:
            l = Location(location = location)
            db.session.add(l)
            db.session.commit()

UploadAreas()
