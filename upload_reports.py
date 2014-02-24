from cm5_app import db
from xlrd import open_workbook
from models import Report
from datetime import datetime

def UploadReport():
    Report.query.delete()

    book = open_workbook('static/uploads/report_data.xls')
    sheet = book.sheet_by_index(0)

    for x in range(0, sheet.nrows):
        date = datetime.strptime(sheet.cell(x,0).value, "%m-%d-%Y")
        bimimg_filename = sheet.cell(x,1).value
        siteimg_filename = sheet.cell(x,2).value
        site_caption = sheet.cell(x,3).value
        summary = sheet.cell(x,4).value
        note = sheet.cell(x,5).value

        r = Report(bimimg_filename = bimimg_filename, siteimg_filename = siteimg_filename, site_caption = site_caption, date = date, note=note, summary=summary)

        db.session.add(r)
        db.session.commit()

UploadReport()
