from flask import render_template, redirect, url_for, flash, Response, request
from cm5_app import app, db, login_manager
from forms import TrackingForm, LoginForm, ReportForm, AddAreaForm, AddShiftForm, AddMaterialForm
from models import Area, Shift, Material, User, Bimlink, Report, Track, Location
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
import uuid
import sx.pisa3 as pisa


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

@app.route("/svg", methods=["GET", "POST"])
def svg():
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

    line_chart = pygal.Line(style=custom_style, label_font_size=14, legend_font_size=14, width=1200, height=400, show_dots=False)
    line_chart.title = 'East Bound Waterproofing (Pits & Walls) Progress Curve'
    line_chart.y_title = '% Complete'
    line_chart.x_labels = map(str, range(2002, 2013))
    line_chart.add('Baseline-Early', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    line_chart.add('Baseline-Late',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
    line_chart.add('Actual',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    svg = line_chart.render()

    return svg

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
#@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/3d")
#@login_required
def threed():
    return render_template('3d.html')

@app.route("/add_area", methods=["GET", "POST"])
#@login_required
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
#@login_required
def add_shift():
        form = AddShiftForm()
        if form.validate_on_submit():
            s = Shift(shift = form.shift.data, start = form.start.data, end = form.end.data)
            db.session.add(s)
            db.session.commit()
            return redirect(url_for('track_waterproofing'))

@app.route("/add_material", methods=["GET", "POST"])
#@login_required
def add_material():
        form = AddMaterialForm()
        if form.validate_on_submit():
            m = Material(material = form.material.data, unit = form.unit.data)
            db.session.add(m)
            db.session.commit()
            return redirect(url_for('track_waterproofing'))

@app.route("/create_waterproofing", methods=["GET", "POST"])
#@login_required
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
        return render_template('create_waterproofing.html', form=form, data_type="Report", action="Add a")

@app.route("/create_waterproofing/<id>/", methods=["GET", "POST"])
#@login_required
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
#@login_required
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
    total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.date))
    return render_template('report_waterproofing.html', i=i, total = total, sums = sums, form=form)

@app.route("/report_waterproofing/<id>", methods=["GET", "POST"])
#@login_required
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
    total = db.session.query(func.sum(Track.quantity).label('total')).join(Area).join(Location).join(Material).filter(Area.id == Track.area_id).filter(Location.id == Track.location_id).filter(Material.id == Track.material_id).filter(Track.date.between(report_date_end, i.date))
    return render_template('report_waterproofing.html', i=i, total = total, sums = sums, form=form)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
#@login_required
def index():
    return render_template('dashboard.html')

@app.route('/track_waterproofing', methods=['GET', 'POST'])
#@login_required
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
        quantity = form.quantity.data)

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
#@login_required
def delete_entry():
    entry = Track.query.order_by(Track.id.desc()).first()
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('track_waterproofing'))

@app.route('/report_as_pdf/<id>', methods=['GET', 'POST'])
#@login_required
def report_as_pdf(id):
    response = Response()
    response.status_code = 200

    data = Report.query.get(id)
    report_date_end = data.date + timedelta(days=-7)
    sums = report_table(data.date, report_date_end)

    pdf = StringIO.StringIO()
    pisa.CreatePDF(StringIO.StringIO(render_template('test_pdf.html', data=data, sums=sums).encode('utf-8')), pdf)
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


@app.route('/download_all_excel', methods=['GET', 'POST'])
#@login_required
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
#@login_required
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

