from flask import render_template, redirect, url_for, flash, Response, request
from cm5_app import app, db, login_manager
from forms import TrackingForm, LoginForm
from models import Track, Area, Shift, Material, User
from datetime import datetime
from flask.ext.login import login_user, login_required, logout_user
import xlwt
import StringIO
import mimetypes
from werkzeug.datastructures import Headers

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
            ))

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

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('dashboard.html')

@app.route("/export_waterproofing", methods=['GET', 'POST'])
@login_required
def export_waterproofing():
    if request.method == 'POST':
        if request.form['submit'] == 'Export All Tracked Waterproofing as Excel':
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

        a = Area.query.filter_by(area = form.area.data).first()
        if a == None:
            a = Area(area = form.area.data, location = form.location.data)
            a.tracks.append(t)
            db.session.add(a)
            db.session.commit()
        else:
            a.tracks.append(t)
            db.session.commit()

        s = Shift.query.filter_by(shift = form.shift.data).first()
        if s == None:
            s = Shift(shift = form.shift.data, start = form.start.data, end = form.end.data)
            s.tracks.append(t)
            db.session.add(s)
            db.session.commit()
        else:
            s.tracks.append(t)
            db.session.commit()

        m = Material.query.filter_by(material = form.material.data).first()
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

    tracks = Track.query.order_by(Track.id.desc()).slice(0,5)
    areas = Area.query.order_by(Area.id)
    shifts = Shift.query.order_by(Shift.id)
    materials = Material.query.order_by(Material.id)
    return render_template('track_waterproofing.html', form=form, tracks=tracks, areas=areas, shifts=shifts, materials=materials)

@app.route('/download_all_excel', methods=['GET', 'POST'])
def download_all_excel():
    response = Response()
    response.status_code = 200

    book = xlwt.Workbook()

    sheet1 = book.add_sheet('Sheet 1')

    tracks = Track.query.order_by(Track.id)
    areas = Area.query.order_by(Area.id)
    shifts = Shift.query.order_by(Shift.id)
    materials = Material.query.order_by(Material.id)
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
    sheet1.row(i).write(9, 'Material')
    sheet1.row(i).write(10, 'Unit')
    sheet1.row(i).write(11, 'Laborer')
    sheet1.row(i).write(12, 'Foreman')
    sheet1.row(i).write(13, 'Super')

    for t in tracks:
        i += 1
        sheet1.row(i).write(0,t.id)
        sheet1.row(i).write(1,str(t.date))
        for s in shifts:
            if s.id == t.shift_id:
                sheet1.row(i).write(2,s.shift)
                sheet1.row(i).write(3,s.start)
                sheet1.row(i).write(4,s.end)
        for a in areas:
            if a.id == t.area_id:
                sheet1.row(i).write(5,a.area)
                sheet1.row(i).write(6,a.location)
        sheet1.row(i).write(7,t.station_start)
        sheet1.row(i).write(8,t.station_end)
        for m in materials:
            if m.id == t.material_id:
                sheet1.row(i).write(9,m.material)
                sheet1.row(i).write(10,m.unit)
        sheet1.row(i).write(11,t.laborer)
        sheet1.row(i).write(12,t.foreman)
        sheet1.row(i).write(13,t.supervisor)


    output = StringIO.StringIO()
    book.save(output)
    response.data = output.getvalue()

    filename = 'ESA CM005 All Waterproofing.xls'
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

