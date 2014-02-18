from flask import render_template, redirect, url_for, flash, Response, request, make_response
from cm5_app import app, db, login_manager
from forms import TrackingForm, LoginForm, WeeklyImgForm, WeeklyForm, AddAreaForm, AddShiftForm, AddMaterialForm
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
import pygal
from pygal.style import Style

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

@app.route("/graph")
def graph():
    custom_style = Style(
        background='transparent',
        plot_background='transparent',
        foreground='#333',
        foreground_light='#666',
        foreground_dark='#222222',
        opacity='.5',
        opacity_hover='.9',
        transition='250ms ease-in',
        colors=(
        'rgb(12,55,149)', 'rgb(117,38,65)', 'rgb(228,127,0)', 'rgb(159,170,0)',
        'rgb(149,12,12)'))

    line_chart = pygal.Line(style=custom_style)
    line_chart.title = 'Browser usage evolution (in %)'
    line_chart.y_title = 'LF Installed'
    line_chart.x_title = 'Date'
    line_chart.x_labels = map(str, range(2002, 2013))
    line_chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    line_chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
    line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,    9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])
    resp = make_response(line_chart.render())

    return resp

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

@app.route("/add_area", methods=["GET", "POST"])
@login_required
def add_area():
    form = AddAreaForm()
    if form.validate_on_submit():
        a = Area(area = form.area.data)
        db.session.add(a)
        l = Location(location = form.location.data)
        db.session.add(l)
        db.session.commit()
        return redirect(url_for('track_waterproofing'))

@app.route("/add_shift", methods=["GET", "POST"])
@login_required
def add_shift():
        form = AddShiftForm()
        if form.validate_on_submit():
            s = Shift(shift = form.shift.data, start = form.start.data, end = form.end.data)
            db.session.add(s)
            db.session.commit()
            return redirect(url_for('track_waterproofing'))

@app.route("/add_material", methods=["GET", "POST"])
@login_required
def add_material():
        form = AddMaterialForm()
        if form.validate_on_submit():
            m = Material(material = form.material.data, unit = form.unit.data)
            db.session.add(m)
            db.session.commit()
            return redirect(url_for('track_waterproofing'))

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
    return render_template('create_waterproofing.html', form=form)

@app.route("/report_waterproofing", methods=["GET", "POST"])
@login_required
def report_waterproofing():
    #get image
    i = Bimimage.query.order_by(Bimimage.id.desc()).first()
    #get image report date - 7 days and query database for entries in that week
    report_date_end = i.report_date + timedelta(days=-7)
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
    #make graph


    total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.report_date))
    return render_template('report_waterproofing.html', i=i, total = total, sums = sums)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/track_waterproofing', methods=['GET', 'POST'])
@login_required
def track_waterproofing():
    form = TrackingForm()
    area_form = AddAreaForm()
    shift_form = AddShiftForm()
    material_form = AddMaterialForm()

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
    return render_template('track_waterproofing.html', form=form, lines=lines, area_form=area_form, shift_form=shift_form, material_form=material_form)

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
                    sheet1.row(i).write(4,li.material.material)
                else:
                    sheet1.row(i).write(1,excel_id)
                    sheet1.row(i).write(2,'Complete')
                    sheet1.row(i).write(3,str(li.date))
                    sheet1.row(i).write(4,li.material.material)
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

