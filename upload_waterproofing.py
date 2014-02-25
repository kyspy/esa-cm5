from cm5_app import db
from xlrd import open_workbook
from models import Track, Area, Material, Shift, Location
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

        t = Track(timestamp = datetime.utcnow(),
        date = date,
        station_start = station_start,
        station_end = station_end,
        quantity = quantity)

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

UploadWaterproofing()
