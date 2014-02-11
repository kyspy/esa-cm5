from flask import render_template, redirect, url_for, flash, Response, request
from cm5_app import app, db, login_manager
from forms import TrackingForm, LoginForm, WeeklyImgForm
from models import Track, Area, Shift, Material, User, Bimlink
from datetime import datetime
from flask.ext.login import login_user, login_required, logout_user
import xlwt
import StringIO
import mimetypes
from werkzeug.datastructures import Headers
from werkzeug.utils import secure_filename

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

@app.route("/3d")
@login_required
def threed():
    return render_template('3d.html')

@app.route("/test_bimlink")
def test_bimlink():
    test = Bimlink.query.order_by(Bimlink.excel_id)
    return render_template('test_bimlink.html', test=test)

@app.route("/bim_upload", methods=["GET", "POST"])
def bim_upload():
    form = WeeklyImgForm()
    return render_template('bim_upload.html', form=form)

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

    lines = Track.query.join(Area).join(Shift).join(Material).filter(Area.id == Track.area_id).filter(Shift.id == Track.shift_id).filter(Material.id == Track.material_id).order_by(Track.id.desc()).slice(0,5)
    return render_template('track_waterproofing.html', form=form, lines=lines)

@app.route('/download_all_excel', methods=['GET', 'POST'])
def download_all_excel():
    response = Response()
    response.status_code = 200

    book = xlwt.Workbook()

    sheet1 = book.add_sheet('Sheet 1')

    lines = Track.query.join(Area).join(Shift).join(Material).filter(Area.id == Track.area_id).filter(Shift.id == Track.shift_id).filter(Material.id == Track.material_id).all()
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
        sheet1.row(i).write(6,li.area.location)
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

    lines = Track.query.join(Area).join(Shift).join(Material).filter(Area.id == Track.area_id).filter(Shift.id == Track.shift_id).filter(Material.id == Track.material_id).all()
    i = 0

    for li in lines:
        start = (int(round(li.station_start*10)*10))
        end = (int(round(li.station_end*10)*10))
        if end > start:
            num = (end - start)/10
            for n in range(0, num):
                s = start + n*10
                e = s+10
                excel_id = li.area.area + '_' + li.area.location + '_' + str(s) + '_' + str(e)
                revit_id = Bimlink.query.filter_by(excel_id = excel_id).first()
                sheet1.row(i).write(0, revit_id.revit_id)
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

