from cm5_app import db
from xlrd import open_workbook
from models import Bimlink

def UploadRevitID():
    book = open_workbook('static/uploads/Revit_ID.xls')
    sheet = book.sheet_by_index(0)
    Bimlink.query.delete()

    for x in range(0, sheet.nrows):
        cell_revit_id = sheet.cell(x,0).value
        cell_excel_id = sheet.cell(x,1).value
        bimlink = Bimlink(revit_id = int(cell_revit_id), excel_id = cell_excel_id)
        db.session.add(bimlink)
        db.session.commit()

UploadRevitID()

