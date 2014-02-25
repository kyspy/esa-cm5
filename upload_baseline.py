from cm5_app import db
from xlrd import open_workbook
from models import Baseline
from datetime import datetime

def UploadBaseline():
    Baseline.query.delete()

    book = open_workbook('static/excel/Baseline_Early_Late.xls')
    sheet = book.sheet_by_index(0)

    for x in range(0, sheet.nrows):
        date = datetime.strptime(sheet.cell(x,0).value, "%Y-%m-%d")
        early = sheet.cell(x,1).value
        late = sheet.cell(x,2).value

        b = Baseline(date = date, early=early, late=late)

        db.session.add(b)
        db.session.commit()

UploadBaseline()
