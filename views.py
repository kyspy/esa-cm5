from flask import render_template, redirect, url_for, flash, Response
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

@app.route("/export_waterproofing")
@login_required
def export_waterproofing():
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

@app.route('/export', methods=['GET', 'POST'])
def export_view():
    #########################
    # Code for creating Flask
    # response
    #########################
    response = Response()
    response.status_code = 200


    ##################################
    # Code for creating Excel data and
    # inserting into Flask response
    ##################################
    book = xlwt.Workbook()

    sheet1 = book.add_sheet('Sheet 1')
    book.add_sheet('Sheet 2')
    sheet1.write(0,0,'A1')
    sheet1.write(0,1,'B1')
    row1 = sheet1.row(1)
    row1.write(0,'A2')
    row1.write(1,'B2')
    sheet1.col(0).width = 10000
    sheet2 = book.get_sheet(1)
    sheet2.row(0).write(0,'Sheet 2 A1')
    sheet2.row(0).write(1,'Sheet 2 B1')
    sheet2.flush_row_data()
    sheet2.write(1,0,'Sheet 2 A3')
    sheet2.col(0).width = 5000
    sheet2.col(0).hidden = True

    output = StringIO.StringIO()
    book.save(output)
    response.data = output.getvalue()

    ################################
    # Code for setting correct
    # headers for jquery.fileDownload
    #################################
    filename = 'export.xls'
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

