from flask import render_template, redirect, url_for, flash
from cm5_app import app, db
from forms import TrackingForm
from models import Track, Area, Shift, Material
from datetime import datetime

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
            ))

@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
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
        flash("The entry has been submitted")
        return redirect(url_for('success'))
    else:
        flash_errors(form)
    return render_template('index.html', form=form)

@app.route('/success', methods=('GET', 'POST'))
def success():
    flash("The entry has been submitted")
    tracks = Track.query.order_by(Track.id)
    areas = Area.query.order_by(Area.id)
    shifts = Shift.query.order_by(Shift.id)
    materials = Material.query.order_by(Material.id)
    return render_template('success.html', tracks=tracks, areas=areas, shifts=shifts, materials=materials)
