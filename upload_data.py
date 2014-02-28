from cm5_app import db
from xlrd import open_workbook
from models import Area, Location, Baseline, Report, Bimlink, Track, Material, Shift
from datetime import datetime

def UploadWaterproofing():
    Track.query.delete()
    Area.query.delete()
    Location.query.delete()
    Material.query.delete()
    Shift.query.delete()

    book = open_workbook('static/excel/waterproofing_data.xls')
    sheet = book.sheet_by_index(0)

    for x in range(0, sheet.nrows):
        date = datetime.strptime(sheet.cell(x,0).value, "%m-%d-%Y")
        shift= sheet.cell(x,1).value
        shift_start= sheet.cell(x,2).value
        shift_end= sheet.cell(x,3).value
        area= sheet.cell(x,4).value
        location= sheet.cell(x,5).value
        material= sheet.cell(x,6).value
        quantity= sheet.cell(x,7).value
        unit= sheet.cell(x,8).value
        station_start= sheet.cell(x,9).value
        station_end= sheet.cell(x,10).value
        img = ""
        caption = ""

        t = Track(
            date = date,
            station_start = station_start,
            station_end = station_end,
            quantity = quantity, img = img, caption = caption)

        a = Area.query.filter_by(area = area).first()
        if a == None:
            a = Area(area = area)
            a.tracks.append(t)
            db.session.add(a)
            db.session.commit()
        else:
            a.tracks.append(t)
            db.session.commit()

        l = Location.query.filter_by(location = location).first()
        if l == None:
            l = Location(location = location)
            l.tracks.append(t)
            db.session.add(l)
            db.session.commit()
        else:
            l.tracks.append(t)
            db.session.commit()

        s = Shift.query.filter_by(shift = shift).first()
        if s == None:
            s = Shift(shift = shift, start = shift_start, end = shift_end)
            s.tracks.append(t)
            db.session.add(s)
            db.session.commit()
        else:
            s.tracks.append(t)
            db.session.commit()

        m = Material.query.filter_by(material = material).first()
        if m == None:
            m = Material(material = material, unit = unit)
            m.tracks.append(t)
            db.session.add(m)
            db.session.commit()
        else:
            m.tracks.append(t)
            db.session.commit()

        db.session.add(t)
        db.session.commit()

def UploadRevitID():
    book = open_workbook('static/excel/Revit_ID.xls')
    sheet = book.sheet_by_index(0)
    Bimlink.query.delete()

    for x in range(0, sheet.nrows):
        cell_revit_id = sheet.cell(x,0).value
        cell_excel_id = sheet.cell(x,1).value
        bimlink = Bimlink(revit_id = int(cell_revit_id), excel_id = cell_excel_id)
        db.session.add(bimlink)
        db.session.commit()

def UploadReport():
    Report.query.delete()

    book = open_workbook('static/excel/report_data.xls')
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

UploadWaterproofing()
UploadReport()
UploadAreas()
UploadBaseline()
UploadRevitID()
