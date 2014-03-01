from flask import render_template, redirect, url_for, flash, Response, request
from cm5_app import app, db, login_manager
from config import basedir
from forms import TrackingForm, LoginForm, ReportForm, AddAreaForm, AddShiftForm, AddMaterialForm, PreviousDateForm
from models import Area, Shift, Material, User, Bimlink, Report, Track, Location, Baseline
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
import uuid
import sx.pisa3 as pisa
from pyvirtualdisplay import Display
from selenium import webdriver

'''
FUNCTIONS***********************************************************************
'''

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

def report_table(date, report_date_end):
    all_areas = Area.query.all()
    all_locations = Location.query.all()
    all_materials = Material.query.all()
    sums = {}
    x = 0
    for a in all_areas:
        for l in all_locations:
            for m in all_materials:
                x += 1
                total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, date)).filter(Material.material == m.material).filter(Area.area == a.area).filter(Location.location == l.location)
                for t in total.all():
                    sums[x] = [a.area, l.location, m.material, t.total]
    return sums

def make_chart(i):
    base = Baseline.query.order_by(Baseline.date).all()
    actual = Track.query.join(Material).filter(Material.id == Track.material_id).order_by(Track.date).all()
    early_list = []
    late_list = []
    actual_list = []
    total = 0
    date_temp=0
    for b in base:
        if b.early:
            early_list.append([b.date.strftime('%Y-%m-%d'), int(b.early)])
    for b in base:
        if b.late:
            late_list.append([b.date.strftime('%Y-%m-%d'), int(b.late)])
    #actual faked for demo there's some calc happening to convert LF to SF and get percentage
    for a in actual:
        if a.material.material == 'Fleece / Geo Drain' and a.date <= i.date:
                if a.date == date_temp:
                    total += int(a.quantity)
                else:
                    total += int(a.quantity)
                    actual_list.append([a.date.strftime('%Y-%m-%d'), int(total/50)])
                    date_temp=a.date

    chart = [{'data': list(early_list),'name': 'Baseline-Early'}, {'data': list(late_list), 'name': 'Baseline-Late'},
        {'data': list(actual_list), 'name': 'Actual'}]

    return chart

'''
LOGIN/ LOGOUT*******************************************************************
'''

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

'''
INDEX***************************************************************************
'''

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('dashboard.html')

'''
TESTING/ PROTOTPYE**************************************************************
'''

@app.route("/3d")
@login_required
def threed():
    return render_template('3d.html')

'''
DAILY REPORT********************************************************************
'''

@app.route("/daily_report", methods=["GET", "POST"])
@login_required
def daily_report():
    form = TrackingForm()
    previous_form = PreviousDateForm()
    today = datetime.today().date()

    if request.method == 'POST':
        id_object = previous_form.previous_date.data
        t = Track.query.filter_by(date = id_object.date).first()
        id = t.id
        return redirect(url_for('daily_report_by_day', id=id))

    t = Track.query.order_by(Track.id.desc()).first()

    if t.date < today:
        entries = None
        id=0
    else:
        id = t.id
        entries = Track.query.join(Area).join(Material).join(Location).filter(Track.date == today).filter(Area.id == Track.area_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).all()
    return render_template('daily_report.html', form=form, entries=entries, today=today, previous_form=previous_form, id=id)

@app.route("/daily_report/<id>/", methods=["GET", "POST"])
@login_required
def daily_report_by_day(id):
    form = TrackingForm()
    previous_form = PreviousDateForm()

    if request.method == 'POST':
        id_object = previous_form.previous_date.data
        t = Track.query.filter_by(date = id_object.date).first()
        id = t.id
        return redirect(url_for('daily_report_by_day', id=id))

    t = Track.query.get(id)
    today = t.date
    entries = Track.query.join(Area).join(Material).join(Location).filter(Track.date == today).filter(Area.id == Track.area_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).all()
    return render_template('daily_report.html', form=form, entries=entries, today = today, previous_form=previous_form, id=id)

@app.route("/add_item", methods=["POST"])
@login_required
def add_item():
    form = TrackingForm()
    if form.validate_on_submit():
        img_file = form.img.data
        if img_file and allowed_file(img_file.filename):
            img_filename = secure_filename(str(uuid.uuid4()) + img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
        else:
            img_filename = ""

        t = Track(date = form.date.data,
        station_start = form.station_start.data,
        station_end = form.station_end.data,
        quantity = form.quantity.data,
        img = img_filename,
        caption = form.caption.data)

        db.session.add(t)

        form_location = form.location.data
        l = Location.query.filter_by(location = form_location.location).first()
        l.tracks.append(t)

        form_area = form.area.data
        a = Area.query.filter(Area.area == form_area.area).first()
        a.tracks.append(t)

        form_material = form.material.data
        m = Material.query.filter_by(material = form_material.material).first()
        m.tracks.append(t)

        db.session.commit()

        return redirect(url_for('daily_report'))
    return str(form.errors)

@app.route('/daily_report_as_pdf/<id>', methods=['GET', 'POST'])
@login_required
def daily_report_as_pdf(id):
    response = Response()
    response.status_code = 200

    t = Track.query.get(id)
    today = t.date
    entries = Track.query.join(Area).join(Material).join(Location).filter(Track.date == today).filter(Area.id == Track.area_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).all()

    pdf = StringIO.StringIO()
    pisa.CreatePDF(StringIO.StringIO(render_template('daily_report_pdf.html', entries=entries, today=today).encode('utf-8')), pdf)
    response.data = pdf.getvalue()

    filename = 'ESA CM005 Daily Report' + t.date.strftime('%Y-%m-%d') + '.pdf'
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

'''
WEEKLY REPORT*******************************************************************
'''

@app.route("/create_waterproofing", methods=["GET", "POST"])
@login_required
def create_waterproofing():
    #figure out how to resize the image
    form = ReportForm()
    if request.method == 'POST':
        if request.form['action'] == 'Upload':
            bim_file = form.bimimg.data
            if bim_file and allowed_file(bim_file.filename):
                bim_filename = secure_filename(str(uuid.uuid4()) + bim_file.filename)
                bim_file.save(os.path.join(app.config['UPLOAD_FOLDER'], bim_filename))
            else:
                bim_filename = ""
            site_file = form.siteimg.data
            if site_file and allowed_file(site_file.filename):
                site_filename = secure_filename(str(uuid.uuid4()) + site_file.filename)
                site_file.save(os.path.join(app.config['UPLOAD_FOLDER'], site_filename))
            else:
                site_filename = ""
            f = Report(bimimg_filename = bim_filename, siteimg_filename = site_filename, site_caption = form.site_caption.data, date = form.date.data, note = form.note.data, summary = form.summary.data)
            db.session.add(f)
            db.session.commit()
            return redirect(url_for('report_waterproofing'))
        elif request.form['action'] == 'Edit':
            id_object = form.edit_date.data
            r = Report.query.get(id_object.id)
            id = r.id
            return redirect(url_for('edit_waterproofing', id=id))
    elif request.method == 'GET':
        return render_template('create_waterproofing.html', form=form, data_type="Weekly Report", action="Add a")

@app.route("/create_waterproofing/<id>/", methods=["GET", "POST"])
@login_required
def edit_waterproofing(id):
    report = Report.query.get(id)
    form = ReportForm(obj=report)
    if request.method == 'POST':
        if request.form['action'] == 'Upload':
            form.populate_obj(report)
            bim_file = form.bimimg.data
            if bim_file and allowed_file(bim_file.filename):
                bim_filename = secure_filename(str(uuid.uuid4()) + bim_file.filename)
                bim_file.save(os.path.join(app.config['UPLOAD_FOLDER'], bim_filename))
                report.bimimg_filename = bim_filename
            site_file = form.siteimg.data
            if site_file and allowed_file(site_file.filename):
                site_filename = secure_filename(str(uuid.uuid4()) + site_file.filename)
                site_file.save(os.path.join(app.config['UPLOAD_FOLDER'], site_filename))
                report.siteimg_filename = site_filename
            report.site_caption = form.site_caption.data
            report.date = form.date.data
            report.note = form.note.data
            report.summary = form.summary.data
            db.session.commit()
            return redirect(url_for('report_waterproofing'))
        elif request.form['action'] == 'Edit':
            id_object = form.edit_date.data
            r = Report.query.get(id_object.id)
            id = r.id
            return redirect(url_for('edit_waterproofing', id=id))
    elif request.method == 'GET':
        return render_template('create_waterproofing.html', form=form, data_type=report.date, action="Edit")

@app.route("/report_waterproofing", methods=["GET", "POST"])
@login_required
def report_waterproofing():
    form = ReportForm()
    if request.method == 'POST':
        id_object = form.edit_date.data
        r = Report.query.get(id_object.id)
        id = r.id
        return redirect(url_for('re_report_waterproofing', id=id))
    i = Report.query.order_by(Report.id.desc()).first()
    report_date_end = i.date + timedelta(days=-7)
    sums = report_table(i.date, report_date_end)
    chart = make_chart(i)
    total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.date))
    total_all= db.session.query(func.sum(Track.quantity).label('total_all')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between('2000-01-01', i.date))
    return render_template('report_waterproofing.html', i=i, total = total, sums = sums, form=form, chart=chart, total_all=total_all)

@app.route("/report_waterproofing/<id>", methods=["GET", "POST"])
@login_required
def re_report_waterproofing(id):
    i = Report.query.get(id)
    form = ReportForm()
    if request.method == 'POST':
        id_object = form.edit_date.data
        r = Report.query.get(id_object.id)
        id = r.id
        return redirect(url_for('re_report_waterproofing', id=id))
    report_date_end = i.date + timedelta(days=-7)
    sums = report_table(i.date, report_date_end)
    chart = make_chart(i)
    total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.date))
    total_all= db.session.query(func.sum(Track.quantity).label('total_all')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between('2000-01-01', i.date))
    return render_template('report_waterproofing.html', i=i, total = total, sums = sums, form=form, chart=chart, total_all=total_all)

@app.route('/report_chart')
def report_chart():
    return render_template('report_chart.html')

@app.route('/report_as_pdf/<id>', methods=['GET', 'POST'])
@login_required
def report_as_pdf(id):
    response = Response()
    response.status_code = 200

    data = Report.query.get(id)
    report_date_end = data.date + timedelta(days=-7)
    sums = report_table(data.date, report_date_end)
    chart = make_chart(data)

    pdf = StringIO.StringIO()
    pisa.CreatePDF(StringIO.StringIO(render_template('test_pdf.html', data=data, sums=sums, chart=chart).encode('utf-8')), pdf)
    response.data = pdf.getvalue()

    filename = 'ESA CM005 Waterproofing Report' + data.date.strftime('%Y-%m-%d') + '.pdf'
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

'''
ORIGINAL TRACKING***************************************************************
'''

@app.route('/track_waterproofing', methods=['GET', 'POST'])
@login_required
def track_waterproofing():
    form = TrackingForm()
    area_form = AddAreaForm()
    shift_form = AddShiftForm()
    material_form = AddMaterialForm()

    if form.validate_on_submit():
        t = Track(
        date = form.date.data,
        station_start = form.station_start.data,
        station_end = form.station_end.data,
        quantity = form.quantity.data,
        img = "", caption = "")

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

@app.route("/add_area", methods=["GET", "POST"])
@login_required
def add_area():
    form = AddAreaForm()
    if form.validate_on_submit():
        a = Area.query.filter_by(area = form.area.data).first()
        if a == None:
            a = Area(area = form.area.data.upper())
            db.session.add(a)
            db.session.commit()

        l = Location.query.filter_by(location = form.location.data).first()
        if l == None:
            l = Location(location = form.location.data.upper())
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
            m = Material.query.filter_by(material = form.material.data).first()
            if m == None:
                m = Material(material = form.material.data, unit = form.unit.data)
                db.session.add(m)
                db.session.commit()
            return redirect(url_for('track_waterproofing'))

@app.route('/delete_entry', methods=['GET', 'POST'])
@login_required
def delete_entry():
    entry = Track.query.order_by(Track.id.desc()).first()
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('track_waterproofing'))

'''
EXCEL DOWNLOAD******************************************************************
'''

@app.route('/download_all_excel', methods=['GET', 'POST'])
@login_required
def download_all_excel():
    response = Response()
    response.status_code = 200

    book = xlwt.Workbook()

    sheet1 = book.add_sheet('Sheet 1')

    lines = Track.query.join(Area).join(Material).join(Location).filter(Area.id == Track.area_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).all()
    i = 0

    sheet1.row(i).write(0,'ID')
    sheet1.row(i).write(1,'Date')
    sheet1.row(i).write(2,'Area')
    sheet1.row(i).write(3,'Location')
    sheet1.row(i).write(4,'Station Start')
    sheet1.row(i).write(5,'Station End')
    sheet1.row(i).write(6,'Quantity')
    sheet1.row(i).write(7, 'Material')
    sheet1.row(i).write(8, 'Unit')
    sheet1.row(i).write(9, 'Img')
    sheet1.row(i).write(10, 'Caption')

    for li in lines:
        i += 1
        sheet1.row(i).write(0,li.id)
        sheet1.row(i).write(1,str(li.date))
        sheet1.row(i).write(2,li.area.area)
        sheet1.row(i).write(3,li.location.location)
        sheet1.row(i).write(4,li.station_start)
        sheet1.row(i).write(5,li.station_end)
        sheet1.row(i).write(6,li.quantity)
        sheet1.row(i).write(7,li.material.material)
        sheet1.row(i).write(8,li.material.unit)
        sheet1.row(i).write(9,li.img)
        sheet1.row(i).write(10,li.caption)

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
@login_required
def download_bim_excel():
    response = Response()
    response.status_code = 200

    date = datetime.utcnow().strftime('%Y-%m-%d')

    book = xlwt.Workbook()
    sheet1 = book.add_sheet('BimLink ' + date)

    lines = Track.query.join(Area).join(Material).join(Location).filter(Area.id == Track.area_id).filter(Material.id == Track.material_id).filter(Location.id == Track.location_id).all()
    i = 0

    for li in lines:
        start = (int(round(li.station_start*10)*10))
        end = (int(round(li.station_end*10)*10))
        #if end > start:
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

