from flask import render_template, redirect, url_for, flash, Response, request
from cm5_app import app, db, login_manager
from forms import TrackingForm, LoginForm, WeeklyImgForm, WeeklyForm
from models import Area, Shift, Material, User, Bimlink, Bimimage, Track, Location
from datetime import datetime, timedelta
from flask.ext.login import login_user, login_required, logout_user
from sqlalchemy import func
import xlwt
import StringIO
import mimetypes
import os
from werkzeug.datastructures import Headers
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
            ))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(email):
    return User.get(email)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get(form.email.data)
        if user and form.password.data == user.password:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/3d")
@login_required
def threed():
    return render_template('3d.html')

@app.route("/test_bimlink")
def test_bimlink():
    test = Bimlink.query.order_by(Bimlink.excel_id)
    return render_template('test_bimlink.html', test=test)

@app.route("/bim_upload", methods=["GET", "POST"])
@login_required
def bim_upload():
    #figure out how to resize the image
    form = WeeklyImgForm()
    form2 = WeeklyForm()
    #upload BIM Image
    if form.validate_on_submit():
        file = form.img.data
        if file and allowed_file(file.filename):
            exists = Bimimage.query.filter_by(report_date = form.date.data).first()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if exists:
                exists.img_filename = file.filename
                db.session.commit()
                return redirect(url_for('report_waterproofing'))
            else:
                f = Bimimage(img_filename = file.filename, report_date = form.date.data)
                db.session.add(f)
                db.session.commit()
                return redirect(url_for('report_waterproofing'))
    #Upload other data

    return render_template('bim_upload.html', form=form)

@app.route("/create_waterproofing", methods=["GET", "POST"])
@login_required
def create_waterproofing():
    #figure out how to resize the image
    form = WeeklyImgForm()
    if form.validate_on_submit():
        file = form.img.data
        if file and allowed_file(file.filename):
            exists = Bimimage.query.filter_by(report_date = form.date.data).first()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if exists:
                exists.img_filename = file.filename
                db.session.commit()
                return redirect(url_for('report_waterproofing'))
            else:
                f = Bimimage(img_filename = file.filename, report_date = form.date.data, report_type = "Waterproofing")
                db.session.add(f)
                db.session.commit()
                return redirect(url_for('report_waterproofing'))
    return render_template('bim_upload.html', form=form)

@app.route("/report_waterproofing", methods=["GET", "POST"])
@login_required
def report_waterproofing():
    #get image
    i = Bimimage.query.order_by(Bimimage.id.desc()).first()
    #get image report date - 7 days and query database for entries in that week
    report_date_end = i.report_date + timedelta(days=-7)
    #temp
    week = Track.query.join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.report_date)).order_by(Area.area)
    #get each area and total quanitity for each area
    all_areas = Area.query.all()
    all_locations = Location.query.all()
    all_materials = Material.query.all()
    sums = {}
    x = 0
    for a in all_areas:
        for l in all_locations:
            for m in all_materials:
                x += 1
                total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.report_date)).filter(Material.material == m.material).filter(Area.area == a.area).filter(Location.location == l.location)
                for t in total.all():
                    sums[x] = [a.area, l.location, m.material, t.total]

    total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.report_date))
    return render_template('report_waterproofing.html', i=i, week=week, total = total, sums = sums)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('dashboard.html')

@app.route("/export_waterproofing", methods=['GET', 'POST'])
@login_required
def export_waterproofing():
    if request.method == 'POST':
        return render_template('export_waterproofing.html')
    elif request.method == 'GET':
        return render_template('export_waterproofing.html')

@app.route('/track_waterproofing', methods=['GET', 'POST'])
@login_required
def track_waterproofing():
    form = TrackingForm()

    if form.validate_on_submit():
        t = Track(timestamp = datetime.utcnow(),
        date = form.date.data,
        station_start = form.station_start.data,
        station_end = form.station_end.data,
        quantity = form.quantity.data,
        laborer = form.laborer.data,
        foreman = form.foreman.data,
        supervisor = form.supervisor.data)

        form_location = form.location.data
        l = Location.query.filter_by(location = form_location.location).first()
        if l == None:
            l = Location(location = form.location.data)
            l.tracks.append(t)
            db.session.add(l)
            db.session.commit()
        else:
            l.tracks.append(t)
            db.session.commit()

        form_area = form.area.data
        a = Area.query.filter(Area.area == form_area.area).first()
        if a == None:
            a = Area(area = form.area.data)
            a.tracks.append(t)
            db.session.add(a)
            db.session.commit()
        else:
            a.tracks.append(t)
            db.session.commit()

        form_shift = form.shift.data
        s = Shift.query.filter(Shift.shift == form_shift.shift).first()
        if s == None:
            s = Shift(shift = form.shift.data, start = form.start.data, end = form.end.data)
            s.tracks.append(t)
            db.session.add(s)
            db.session.commit()
        else:
            s.tracks.append(t)
            db.session.commit()

        form_material = form.material.data
        m = Material.query.filter_by(material = form_material.material).first()
        if m == None:
            m = Material(material = form.material.data, unit = form.unit.data)
            m.tracks.append(t)
            db.session.add(m)
            db.session.commit()
        else:
            m.tracks.append(t)
            db.session.commit()

        db.session.add(t)
        db.session.commit()
        return redirect(url_for('track_waterproofing'))

    lines = Track.query.join(Area).join(Shift).join(Material).join(Location).filter(Area.id == Track.area_id).filter(Shift.id == Track.shift_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).order_by(Track.id.desc()).slice(0,5)
    return render_template('track_waterproofing.html', form=form, lines=lines)

@app.route('/delete_entry', methods=['GET', 'POST'])
@login_required
def delete_entry():
    entry = Track.query.order_by(Track.id.desc()).first()
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('track_waterproofing'))

@app.route('/download_all_excel', methods=['GET', 'POST'])
def download_all_excel():
    response = Response()
    response.status_code = 200

    book = xlwt.Workbook()

    sheet1 = book.add_sheet('Sheet 1')

    lines = Track.query.join(Area).join(Shift).join(Material).join(Location).filter(Area.id == Track.area_id).filter(Shift.id == Track.shift_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).all()
    i = 0

    sheet1.row(i).write(0,'ID')
    sheet1.row(i).write(1,'Date')
    sheet1.row(i).write(2,'Shift')
    sheet1.row(i).write(3,'Shift Start')
    sheet1.row(i).write(4,'Shift End')
    sheet1.row(i).write(5,'Area')
    sheet1.row(i).write(6,'Location')
    sheet1.row(i).write(7,'Station Start')
    sheet1.row(i).write(8,'Station End')
    sheet1.row(i).write(9,'Quantity')
    sheet1.row(i).write(10, 'Material')
    sheet1.row(i).write(11, 'Unit')
    sheet1.row(i).write(12, 'Laborer')
    sheet1.row(i).write(13, 'Foreman')
    sheet1.row(i).write(14, 'Super')

    for li in lines:
        i += 1
        sheet1.row(i).write(0,li.id)
        sheet1.row(i).write(1,str(li.date))
        sheet1.row(i).write(2,li.shift.shift)
        sheet1.row(i).write(3,li.shift.start)
        sheet1.row(i).write(4,li.shift.end)
        sheet1.row(i).write(5,li.area.area)
        sheet1.row(i).write(6,li.location.location)
        sheet1.row(i).write(7,li.station_start)
        sheet1.row(i).write(8,li.station_end)
        sheet1.row(i).write(9,li.quantity)
        sheet1.row(i).write(10,li.material.material)
        sheet1.row(i).write(11,li.material.unit)
        sheet1.row(i).write(12,li.laborer)
        sheet1.row(i).write(13,li.foreman)
        sheet1.row(i).write(14,li.supervisor)


    output = StringIO.StringIO()
    book.save(output)
    response.data = output.getvalue()

    filename = 'ESA CM005 Waterproofing_' + datetime.utcnow().strftime('%Y-%m-%d') + '.xls'
    mimetype_tuple = mimetypes.guess_type(filename)

    #HTTP headers for forcing file download
    response_headers = Headers({
            'Pragma': "public",  # required,
            'Expires': '0',
            'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
            'Cache-Control': 'private',  # required for certain browsers,
            'Content-Type': mimetype_tuple[0],
            'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
            'Content-Transfer-Encoding': 'binary',
            'Content-Length': len(response.data)
        })

    if not mimetype_tuple[1] is None:
        response.update({
                'Content-Encoding': mimetype_tuple[1]
            })

    response.headers = response_headers

    #as per jquery.fileDownload.js requirements
    response.set_cookie('fileDownload', 'true', path='/')

    return response

@app.route('/download_bim_excel', methods=['GET', 'POST'])
def download_bim_excel():
    response = Response()
    response.status_code = 200

    date = datetime.utcnow().strftime('%Y-%m-%d')

    book = xlwt.Workbook()
    sheet1 = book.add_sheet('BimLink ' + date)

    lines = Track.query.join(Area).join(Shift).join(Material).join(Location).filter(Area.id == Track.area_id).filter(Shift.id == Track.shift_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).all()
    i = 0

    for li in lines:
        start = (int(round(li.station_start*10)*10))
        end = (int(round(li.station_end*10)*10))
        if end > start:
            num = (end - start)/10
            for n in range(0, num):
                s = start + n*10
                e = s+10
                excel_id = li.area.area + '_' + li.location.location + '_' + str(s) + '_' + str(e)
                revit_id = Bimlink.query.filter_by(excel_id = excel_id).first()
                if revit_id:
                    sheet1.row(i).write(0, revit_id.revit_id)
                    sheet1.row(i).write(1,excel_id)
                    sheet1.row(i).write(2,'Complete')
                    sheet1.row(i).write(3,str(li.date))
                else:
                    sheet1.row(i).write(1,excel_id)
                    sheet1.row(i).write(2,'Complete')
                    sheet1.row(i).write(3,str(li.date))
                i += 1

    output = StringIO.StringIO()
    book.save(output)
    response.data = output.getvalue()

    filename = 'ESA CM005 Waterproofing BIMLink_' + date + '.xls'
    mimetype_tuple = mimetypes.guess_type(filename)

    #HTTP headers for forcing file download
    response_headers = Headers({
            'Pragma': "public",  # required,
            'Expires': '0',
            'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
            'Cache-Control': 'private',  # required for certain browsers,
            'Content-Type': mimetype_tuple[0],
            'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
            'Content-Transfer-Encoding': 'binary',
            'Content-Length': len(response.data)
        })

    if not mimetype_tuple[1] is None:
        response.update({
                'Content-Encoding': mimetype_tuple[1]
            })

    response.headers = response_headers

    #as per jquery.fileDownload.js requirements
    response.set_cookie('fileDownload', 'true', path='/')

    return response

